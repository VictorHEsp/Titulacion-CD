"""Motor de optimización ECOBICI, basado en Optimizacion_v1.ipynb.

Trabaja con datos ya preparados en el notebook; NO reentrena el predictor.
Las distancias son euclidianas sobre EPSG:32614 (metros).
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


@dataclass
class MotorEcobici:
    candidatas: object  # GeoDataFrame en EPSG:32614 y orden idx_modelo
    cobertura: csr_matrix
    habitantes: np.ndarray
    grafo: csr_matrix
    distancia_minima: float = 250.0
    distancia_conexion: float = 500.0

    def __post_init__(self):
        n = len(self.candidatas)
        if self.cobertura.shape != (n, len(self.habitantes)):
            raise ValueError('Dimensiones de matriz_cobertura inconsistentes con las candidatas.')
        if self.grafo.shape != (n, n):
            raise ValueError('Dimensiones del grafo inconsistentes.')
        self.ids = self.candidatas['id_celda'].to_numpy()
        self.coords = np.column_stack((self.candidatas.geometry.x, self.candidatas.geometry.y))
        self.dist_existente = self.candidatas['dist_ecobici_min'].to_numpy(dtype=float)
        self.elegibles = self.dist_existente >= self.distancia_minima
        self.demanda = self.candidatas['demanda_rf'].to_numpy(dtype=float)
        self.manzanas = [self.cobertura.getrow(i).indices for i in range(n)]
        self.escala_poblacion = float(np.percentile(
            self.candidatas.loc[self.elegibles, 'poblacion_incremental'], 95))
        self.escala_demanda = float(np.percentile(self.demanda[self.elegibles], 95))
        if self.escala_poblacion <= 0 or self.escala_demanda <= 0:
            raise ValueError('Escalas de normalización no positivas.')

    def _nucleo(self, semilla, factibles, restantes, tamano, wp, wd):
        if not factibles[semilla]:
            return None
        grupo = [int(semilla)]
        cubiertas = np.zeros(len(self.habitantes), dtype=bool)
        cubiertas[self.manzanas[semilla]] = True

        while len(grupo) < tamano:
            vecinos = np.unique(np.concatenate([
                self.grafo.indices[self.grafo.indptr[i]:self.grafo.indptr[i+1]]
                for i in grupo
            ]))
            vecinos = vecinos[factibles[vecinos] & ~np.isin(vecinos, grupo)]
            if not len(vecinos):
                return None
            distancias = np.linalg.norm(
                self.coords[vecinos, None, :] - self.coords[np.array(grupo)][None, :, :],
                axis=2
            )
            vecinos = vecinos[(distancias >= self.distancia_minima).all(axis=1)]
            if not len(vecinos):
                return None
            puntajes = []
            for vecino in vecinos:
                man = self.manzanas[vecino]
                nueva = restantes[man[~cubiertas[man]]].sum()
                puntajes.append(
                    wp * nueva / self.escala_poblacion
                    + wd * self.demanda[vecino] / self.escala_demanda
                )
            mejor = int(vecinos[np.argmax(puntajes)])
            grupo.append(mejor)
            cubiertas[self.manzanas[mejor]] = True

        man = np.flatnonzero(cubiertas)
        beneficio = (wp * restantes[man].sum() / self.escala_poblacion
                     + wd * self.demanda[grupo].sum() / self.escala_demanda)
        return {'indices': grupo, 'puntaje_por_estacion': beneficio / len(grupo)}

    def optimizar(self, K=10, peso_cobertura=0.65, alcaldia=None,
                 estrategia='Mixta', minimo_nucleo=5):
        if not isinstance(K, (int, np.integer)) or K < 10 or K > len(self.ids):
            raise ValueError('K debe ser un entero entre 10 y el número de candidatas.')
        if not 0 <= peso_cobertura <= 1:
            raise ValueError('El peso de cobertura debe estar entre 0 y 1.')
        if estrategia not in ('Mixta', 'Solo conectada'):
            raise ValueError('Estrategia no válida.')
        if not isinstance(minimo_nucleo, (int, np.integer)) or minimo_nucleo < 3:
            raise ValueError('Tamaño mínimo de núcleo inválido.')
        if alcaldia is None:
            mascara = np.ones(len(self.ids), dtype=bool)
        else:
            if alcaldia not in self.candidatas['alcaldia'].dropna().unique():
                raise ValueError(f'Alcaldía no encontrada: {alcaldia}')
            mascara = (self.candidatas['alcaldia'] == alcaldia).to_numpy()

        wp, wd = float(peso_cobertura), 1.0 - float(peso_cobertura)
        restantes = self.habitantes.copy()
        seleccionados = []
        dist_nuevas = np.full(len(self.ids), np.inf)
        filas = []
        bloque = 0

        while len(seleccionados) < K:
            disponibles = K - len(seleccionados)
            factibles = self.elegibles & mascara & (dist_nuevas >= self.distancia_minima)
            factibles[seleccionados] = False
            ganancias = np.asarray(self.cobertura @ restantes).ravel()
            puntajes = (wp * ganancias / self.escala_poblacion
                        + wd * self.demanda / self.escala_demanda)
            conectables = ((self.dist_existente <= self.distancia_conexion)
                           | (dist_nuevas <= self.distancia_conexion))
            puntajes_ind = puntajes.copy()
            puntajes_ind[~(factibles & conectables)] = -np.inf
            idx = int(np.argmax(puntajes_ind))
            mejor_puntaje = float(puntajes_ind[idx])
            mejor_grupo = [idx] if np.isfinite(mejor_puntaje) else []
            tipo = 'Extensión'

            if estrategia == 'Mixta' and disponibles >= minimo_nucleo:
                nucleo_factible = (factibles
                                   & (self.dist_existente > self.distancia_conexion)
                                   & (dist_nuevas > self.distancia_conexion))
                ranking = np.argsort(puntajes)[::-1]
                semillas = []
                for i in ranking:
                    if not nucleo_factible[i]:
                        continue
                    if semillas and (np.linalg.norm(
                        self.coords[semillas] - self.coords[i], axis=1) < 800
                    ).any():
                        continue
                    semillas.append(int(i))
                    if len(semillas) == 60:
                        break
                for semilla in semillas:
                    nucleo = self._nucleo(semilla, nucleo_factible, restantes,
                                          minimo_nucleo, wp, wd)
                    if nucleo and nucleo['puntaje_por_estacion'] > mejor_puntaje:
                        mejor_puntaje = nucleo['puntaje_por_estacion']
                        mejor_grupo = nucleo['indices']
                        tipo = 'Nuevo núcleo'

            if not mejor_grupo:
                raise ValueError('No hay suficientes estaciones factibles para este K y filtro.')
            bloque += 1
            for i in mejor_grupo:
                man = self.manzanas[i]
                ganancia = float(restantes[man].sum())
                filas.append({
                    'bloque': bloque, 'tipo': tipo,
                    'id_celda': int(self.ids[i]),
                    'poblacion_adicional': ganancia,
                    'demanda_rf': float(self.demanda[i]),
                })
                restantes[man] = 0
                seleccionados.append(i)
            distancia = np.linalg.norm(
                self.coords[:, None, :] - self.coords[mejor_grupo][None, :, :],
                axis=2
            ).min(axis=1)
            dist_nuevas = np.minimum(dist_nuevas, distancia)

        resultado = pd.DataFrame(filas)
        self.validar_resultado(resultado, minimo_nucleo, alcaldia)
        return resultado

    def validar_resultado(self, resultado, minimo_nucleo, alcaldia):
        indices = pd.Index(self.ids).get_indexer(resultado['id_celda'])
        if (indices < 0).any() or len(set(indices)) != len(indices):
            raise ValueError('IDs faltantes o repetidos en la solución.')
        if alcaldia is not None and not (self.candidatas.iloc[indices]['alcaldia'] == alcaldia).all():
            raise ValueError('La solución contiene estaciones fuera de la alcaldía solicitada.')
        d = np.linalg.norm(self.coords[indices, None] - self.coords[indices][None], axis=2)
        if (d[np.triu_indices(len(indices), 1)] < self.distancia_minima - 1e-8).any():
            raise ValueError('La solución incumple la separación mínima.')
        conexiones = (d <= self.distancia_conexion) & (d > 0)
        ncomp, comp = connected_components(csr_matrix(conexiones), directed=False)
        for i in range(ncomp):
            miembros = indices[comp == i]
            if not (self.dist_existente[miembros] <= self.distancia_conexion).any() and len(miembros) < minimo_nucleo:
                raise ValueError('Núcleo independiente demasiado pequeño.')

    def clasificar_componentes(self, resultado):
        """Clasificación final (no confundir con el tipo de acción de construcción)."""
        indices = pd.Index(self.ids).get_indexer(resultado['id_celda'])
        d = np.linalg.norm(self.coords[indices, None] - self.coords[indices][None], axis=2)
        ncomp, etiqueta = connected_components(
            csr_matrix((d <= self.distancia_conexion) & (d > 0)), directed=False)
        tipos = {}
        for comp in range(ncomp):
            miembros = indices[etiqueta == comp]
            tipos[comp] = ('Conectada a ECOBICI'
                           if (self.dist_existente[miembros] <= self.distancia_conexion).any()
                           else 'Núcleo independiente')
        salida = resultado.copy()
        salida['componente'] = etiqueta + 1
        salida['tipo_red'] = [tipos[i] for i in etiqueta]
        return salida
