"""SN-3 — Reproducción rápida a partir de los datos procesados de ECOBICI.

Desde la raíz del repositorio, ejecutar:
    python scripts/quick.py

Para incluir las tres búsquedas anidadas (más lentas):
    python scripts/quick.py --all-models

Salidas: outputs/quick/{tabla_modelos.csv,mae_rf_por_fold.csv,
                      tabla_escenarios.csv,recomendaciones_*.csv,
                      figura_mae.png,figura_escenarios.png}

NOTA: No reconstituye los CSV de viajes crudos, ni recalcula la predicción
para 12,954 candidatas. Utiliza datos_modelo_ECOBICI.csv y los seis archivos
ya exportados al tablero. El motor SÍ vuelve a optimizar desde esos insumos.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")  # Funciona también dentro de Docker, sin pantalla.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.sparse import load_npz
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GroupKFold, GridSearchCV, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from src.motor_ecobici import MotorEcobici

DATA = ROOT / "data" / "processed"
TABLERO = DATA / "tablero"
OUTPUT = ROOT / "outputs" / "quick"

PREDICTORAS = [
    "poblacion_500m", "negocios_500m", "personal_500m",
    "dist_metro", "dist_metrobus", "infra_ciclista_500m",
    "estaciones_ecobici_500m", "universidades_500m", "dist_centro",
]

# Referencias fijas: SOLAMENTE para pruebas automáticas, nunca como resultados
# del algoritmo. Se obtuvieron de Optimizacion_v1, celdas 36 y 49.
REFERENCIAS = {
    "Solo conectada": {
        "ids": [16988, 16793, 17199, 17192, 17194, 17600, 17401, 17807, 17599, 17809],
        "poblacion": 94496,
        "movimientos": 2063.57,
        "nucleos": 0,
    },
    "Mixta": {
        "ids": [17600, 17194, 17599, 17196, 17198, 18616, 19022, 19020, 19024, 19026],
        "poblacion": 157606,
        "movimientos": 1634.93,
        "nucleos": 2,
    },
}


def comprobar(archivo: Path) -> None:
    if not archivo.is_file():
        raise FileNotFoundError(
            f"No se encuentra {archivo.relative_to(ROOT)}. "
            "Revisa que esté incluido en el repositorio."
        )


def evaluar_modelos(todos: bool) -> None:
    """Reconstruir la tabla de MAE por fold a partir de las 670 estaciones."""
    archivo = DATA / "datos_modelo_ECOBICI.csv"
    comprobar(archivo)
    datos = pd.read_csv(archivo)
    X = datos[PREDICTORAS].copy()
    y = datos["movimientos_diarios"].copy()
    if len(datos) != 670 or X.isna().any().any() or y.isna().any():
        raise AssertionError("Datos de entrenamiento incompletos o distintos a las 670 estaciones.")

    # Mismos bloques que Modelado_v1: origen en mínimos de coordenadas EPSG:32614.
    geo = gpd.GeoDataFrame(
        datos, geometry=gpd.points_from_xy(datos.longitud, datos.latitud),
        crs="EPSG:4326",
    ).to_crs(epsg=32614)
    gx = ((geo.geometry.x - geo.geometry.x.min()) // 2000).astype(int)
    gy = ((geo.geometry.y - geo.geometry.y.min()) // 2000).astype(int)
    grupos = gx.astype(str) + "_" + gy.astype(str)
    if grupos.nunique() != 28:
        raise AssertionError(f"Se esperaban 28 bloques espaciales; se encontraron {grupos.nunique()}.")
    cv = GroupKFold(n_splits=5)

    rf = RandomForestRegressor(
        n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1,
    )
    gb = GradientBoostingRegressor(
        n_estimators=200, learning_rate=0.05, max_depth=2,
        min_samples_leaf=5, random_state=42,
    )
    poli_exploratoria = make_pipeline(
        StandardScaler(), PolynomialFeatures(degree=2, include_bias=False),
        Ridge(alpha=100),
    )

    modelos = [
        ("Base (mediana)", "Fijo", DummyRegressor(strategy="median")),
        ("Regresión lineal", "Fijo", make_pipeline(StandardScaler(), LinearRegression())),
        ("Ridge", "Fijo", make_pipeline(StandardScaler(), Ridge(alpha=10))),
        ("Random Forest", "Fijo", rf),
        ("Gradient Boosting", "Fijo", gb),
    ]
    try:
        from xgboost import XGBRegressor
        modelos.append((
            "XGBoost", "Fijo",
            XGBRegressor(n_estimators=300, max_depth=3, learning_rate=0.05,
                         subsample=0.8, colsample_bytree=0.8,
                         objective="reg:squarederror", random_state=42, n_jobs=1),
        ))
    except ImportError as exc:
        raise ImportError("Falta xgboost, incluido en requirements.txt") from exc
    modelos.append(("Ridge polinómica", "Exploratorio", poli_exploratoria))

    resumen = []
    errores_por_modelo = {}

    def agregar(nombre: str, protocolo: str, errores) -> None:
        errores = np.asarray(errores, dtype=float)
        if errores.shape != (5,) or not np.isfinite(errores).all():
            raise AssertionError(f"Errores inválidos para {nombre}")
        errores_por_modelo[nombre] = errores
        resumen.append({
            "Modelo": nombre, "Protocolo": protocolo,
            "MAE medio": float(errores.mean()),
            **{f"Fold {i + 1}": float(e) for i, e in enumerate(errores)},
            "Desviación": float(errores.std(ddof=0)),
        })
        print(f"  {nombre:<29} MAE medio {errores.mean():.2f}")

    print("\n1/3  Evaluando modelos con GroupKFold (5 folds; 28 bloques)…", flush=True)
    for nombre, protocolo, estimador in modelos:
        scores = -cross_val_score(
            estimador, X, y, cv=cv, groups=grupos,
            scoring="neg_mean_absolute_error", n_jobs=1,
        )
        agregar(nombre, protocolo, scores)

    # Comprobación central de las cifras del manuscrito; un cambio relevante falla.
    for nombre, esperado in [("Base (mediana)", 70.69), ("Random Forest", 56.67)]:
        obtenido = errores_por_modelo[nombre].mean()
        if not np.isclose(obtenido, esperado, atol=0.20, rtol=0):
            raise AssertionError(
                f"MAE {nombre} = {obtenido:.3f}, esperado ~{esperado:.2f}. "
                "Revisar versiones, datos y división espacial."
            )

    if todos:
        print("\n  Calculando las tres búsquedas anidadas (tardan más)…", flush=True)
        anidados = [
            ("RF optimizado", GridSearchCV(
                RandomForestRegressor(random_state=42, n_jobs=1),
                param_grid={"n_estimators": [150, 300], "max_depth": [None, 10],
                            "min_samples_leaf": [3, 7]},
                scoring="neg_mean_absolute_error", cv=GroupKFold(n_splits=3), n_jobs=1,
            )),
            ("GB optimizado", GridSearchCV(
                GradientBoostingRegressor(min_samples_leaf=5, random_state=42),
                param_grid={"n_estimators": [100, 200],
                            "learning_rate": [0.05, 0.1], "max_depth": [2, 3]},
                scoring="neg_mean_absolute_error", cv=GroupKFold(n_splits=3), n_jobs=1,
            )),
            ("Ridge polinómica optimizada", GridSearchCV(
                make_pipeline(StandardScaler(),
                              PolynomialFeatures(degree=2, include_bias=False),
                              StandardScaler(), Ridge()),
                param_grid={"ridge__alpha": [1, 10, 100, 1000]},
                scoring="neg_mean_absolute_error", cv=GroupKFold(n_splits=3), n_jobs=1,
            )),
        ]
        for nombre, busqueda in anidados:
            errores = []
            for train, test in cv.split(X, y, groups=grupos):
                busqueda.fit(X.iloc[train], y.iloc[train], groups=grupos.iloc[train])
                pred = busqueda.predict(X.iloc[test])
                errores.append(mean_absolute_error(y.iloc[test], pred))
            agregar(nombre, "Anidado", errores)

    tabla = pd.DataFrame(resumen)
    tabla.to_csv(OUTPUT / "tabla_modelos.csv", index=False, float_format="%.6f")
    rf_errores = pd.DataFrame({
        "Fold": np.arange(1, 6),
        "MAE_base": errores_por_modelo["Base (mediana)"],
        "MAE_RF": errores_por_modelo["Random Forest"],
    })
    rf_errores.to_csv(OUTPUT / "mae_rf_por_fold.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(rf_errores["Fold"], rf_errores["MAE_base"], "o-", label="Base (mediana)")
    ax.plot(rf_errores["Fold"], rf_errores["MAE_RF"], "s-", label="Random Forest")
    ax.set(xlabel="Partición espacial", ylabel="MAE (movimientos diarios)",
           title="Error de validación espacial por partición")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT / "figura_mae.png", dpi=180)
    plt.close(fig)


def evaluar_escenarios() -> None:
    """Optimizar de nuevo y fallar si cambian los 10 IDs o resultados de referencia."""
    for nombre in ["candidatas.gpkg", "matriz_cobertura.npz", "habitantes.npy", "grafo.npz"]:
        comprobar(TABLERO / nombre)
    candidatas = (gpd.read_file(TABLERO / "candidatas.gpkg")
                  .sort_values("idx_modelo").reset_index(drop=True))
    motor = MotorEcobici(
        candidatas=candidatas,
        cobertura=load_npz(TABLERO / "matriz_cobertura.npz").tocsr(),
        habitantes=np.load(TABLERO / "habitantes.npy"),
        grafo=load_npz(TABLERO / "grafo.npz").tocsr(),
    )
    if len(candidatas) != 12954:
        raise AssertionError(f"Se esperaban 12,954 candidatas, hay {len(candidatas)}.")
    print("\n2/3  Recalculando las estrategias K=10, pesos 65/35…", flush=True)

    filas = []
    for nombre, esperado in REFERENCIAS.items():
        resultado = motor.optimizar(
            K=10, peso_cobertura=0.65, estrategia=nombre,
            minimo_nucleo=5,
        )
        clasificado = motor.clasificar_componentes(resultado)
        ids = resultado["id_celda"].astype(int).tolist()
        poblacion = float(resultado["poblacion_adicional"].sum())
        movimientos = float(resultado["demanda_rf"].sum())
        nucleos = int(clasificado.loc[
            clasificado["tipo_red"] == "Núcleo independiente", "componente",
        ].nunique())

        if ids != esperado["ids"]:
            raise AssertionError(f"{nombre}: cambiaron las 10 cuadrículas o su orden: {ids}")
        if not np.isclose(poblacion, esperado["poblacion"], atol=0.01, rtol=0):
            raise AssertionError(f"{nombre}: población {poblacion} != {esperado['poblacion']}")
        if not np.isclose(movimientos, esperado["movimientos"], atol=0.02, rtol=0):
            raise AssertionError(f"{nombre}: movimientos {movimientos} != {esperado['movimientos']}")
        if nucleos != esperado["nucleos"]:
            raise AssertionError(f"{nombre}: núcleos {nucleos} != {esperado['nucleos']}")

        resultado.to_csv(
            OUTPUT / ("recomendaciones_" + nombre.lower().replace(" ", "_") + ".csv"),
            index=False,
        )
        filas.append({
            "Estrategia": nombre, "K": 10, "Peso cobertura": 0.65,
            "Población adicional": poblacion,
            "Movimientos diarios predichos": movimientos,
            "Núcleos independientes": nucleos,
        })
        print(f"  {nombre:<17} población={poblacion:.0f}; "
              f"movimientos={movimientos:.2f}; núcleos={nucleos}; IDs: OK")

    tabla = pd.DataFrame(filas)
    tabla.to_csv(OUTPUT / "tabla_escenarios.csv", index=False)
    fig, axes = plt.subplots(figsize=(8, 4.8))
    labels = tabla["Estrategia"].tolist()
    # Ejes separados para dos unidades distintas: evitar compararlas en una escala única.
    ax1 = axes
    x = np.arange(len(labels))
    ax1.bar(x - 0.18, tabla["Población adicional"], width=0.36, label="Población")
    ax1.set_ylabel("Población adicional (habitantes)")
    ax1.set_xticks(x, labels)
    ax2 = ax1.twinx()
    ax2.plot(x + 0.18, tabla["Movimientos diarios predichos"], "ko", markersize=9,
             label="Movimientos")
    ax2.set_ylabel("Movimientos diarios predichos")
    ax1.set_title("Comparación de estrategias de expansión (K=10, 65/35)")
    fig.tight_layout()
    fig.savefig(OUTPUT / "figura_escenarios.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-models", action="store_true",
                        help="También recalcula las tres búsquedas anidadas del apéndice.")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    evaluar_modelos(todos=args.all_models)
    evaluar_escenarios()
    print("\n3/3  OK: modelos, escenarios, figuras y 10 IDs verificados.")
    print(f"Resultados: {OUTPUT.relative_to(ROOT)}/")
    if not args.all_models:
        print("Nota: las 3 configuraciones anidadas se pueden reproducir con --all-models.")


if __name__ == "__main__":
    main()
