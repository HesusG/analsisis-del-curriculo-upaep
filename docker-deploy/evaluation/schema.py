"""Pydantic models matching the JSON output schema in analisis_planeacion/rules.md."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────

class NivelGeneral(str, Enum):
    SATISFACTORIO = "Satisfactorio"
    EN_PROCESO = "En proceso"
    REQUIERE_ATENCION = "Requiere atención"


# ── Reusable blocks ───────────────────────────────────────────────────

class Criterio(BaseModel):
    criterio: str
    cumple: bool
    observacion: str = ""
    evidencia: str = ""  # fragmento citado del documento fuente


class SubBloque(BaseModel):
    """Block that may or may not apply (e.g. competencias)."""
    aplica: bool
    criterios: list[Criterio] = Field(default_factory=list)


class FaseMejora(BaseModel):
    nombre: str
    descripcion: str
    acciones: list[str] = Field(min_length=1)


# ── Part models ────────────────────────────────────────────────────────

class Metadata(BaseModel):
    evaluador: str
    institucion: str
    responsable_planeacion: str
    fecha_evaluacion: str


class DiagnosticoInstitucion(BaseModel):
    necesidades: str
    modelo_ensenanza: str
    filosofia: str


class DiagnosticoEstudiantes(BaseModel):
    numero_estudiantes: str
    grupos: str
    niveles_modalidades: str


class Parte1Contexto(BaseModel):
    diagnostico_institucion: DiagnosticoInstitucion
    diagnostico_estudiantes: DiagnosticoEstudiantes
    descripcion_general: str


class Parte2DatosPresentacion(BaseModel):
    criterios: list[Criterio]


class Parte3PropositoObjetivo(BaseModel):
    criterios: list[Criterio]
    recomendaciones: str = ""


class Parte4CompetenciasAprendizajes(BaseModel):
    rubros_encontrados: list[str] = Field(default_factory=list)
    competencias: SubBloque
    aprendizajes_esperados: SubBloque


class Parte5Contenidos(BaseModel):
    descripcion_general: str
    tipo_contenido_predominante: str
    criterios: list[Criterio]


class FasesDidacticas(BaseModel):
    inicio: bool
    procesamiento: bool
    reforzamiento: bool
    sistematizacion_cierre: bool


class Parte6Secuencia(BaseModel):
    descripcion_general: str
    fases_didacticas: FasesDidacticas
    recomendaciones: str = ""


class Parte7Metodologia(BaseModel):
    descripcion_general: str
    criterios: list[Criterio]


class TiposEvaluacion(BaseModel):
    diagnostica: bool
    formativa: bool
    sumativa: bool


class Parte8Evaluacion(BaseModel):
    descripcion_general: str
    tipos_evaluacion: TiposEvaluacion
    criterios: list[Criterio]


class Parte9Recursos(BaseModel):
    descripcion_general: str
    tipo_recursos: str = ""
    recomendaciones: str = ""


class Parte10Conclusiones(BaseModel):
    areas_oportunidad: list[str] = Field(min_length=1)
    recomendaciones_redaccion: str
    recomendaciones_innovacion: str
    herramientas_digitales_sugeridas: list[str] = Field(min_length=1)


class Parte11PropuestaMejora(BaseModel):
    fases: list[FaseMejora]


class ResumenEjecutivo(BaseModel):
    criterios_cumplidos: int
    criterios_no_cumplidos: int
    porcentaje_cumplimiento: float
    nivel_general: NivelGeneral
    fortalezas_principales: list[str] = Field(min_length=1)
    areas_criticas: list[str] = Field(min_length=1)


# ── Full evaluation ───────────────────────────────────────────────────

class FullEvaluation(BaseModel):
    """Complete evaluation output matching rules.md JSON schema."""
    metadata: Metadata
    parte_1_contexto: Parte1Contexto
    parte_2_datos_presentacion: Parte2DatosPresentacion
    parte_3_proposito_objetivo: Parte3PropositoObjetivo
    parte_4_competencias_aprendizajes: Parte4CompetenciasAprendizajes
    parte_5_contenidos: Parte5Contenidos
    parte_6_secuencia: Parte6Secuencia
    parte_7_metodologia: Parte7Metodologia
    parte_8_evaluacion: Parte8Evaluacion
    parte_9_recursos: Parte9Recursos
    parte_10_conclusiones: Parte10Conclusiones
    parte_11_propuesta_mejora: Parte11PropuestaMejora
    resumen_ejecutivo: ResumenEjecutivo

    def count_criteria(self) -> tuple[int, int]:
        """Count (passed, failed) criteria across parts 2-8."""
        passed = failed = 0
        for part_name in [
            "parte_2_datos_presentacion",
            "parte_3_proposito_objetivo",
            "parte_5_contenidos",
            "parte_7_metodologia",
            "parte_8_evaluacion",
        ]:
            for c in getattr(self, part_name).criterios:
                if c.cumple:
                    passed += 1
                else:
                    failed += 1
        # parte_4 has sub-blocks
        for sub in [
            self.parte_4_competencias_aprendizajes.competencias,
            self.parte_4_competencias_aprendizajes.aprendizajes_esperados,
        ]:
            if sub.aplica:
                for c in sub.criterios:
                    if c.cumple:
                        passed += 1
                    else:
                        failed += 1
        return passed, failed
