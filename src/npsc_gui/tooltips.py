from __future__ import annotations


BRIEF_TOOLTIPS = {
    "compile": "Mejorar prompt",
    "copy": "Copiar prompt listo",
    "copy_json": "Copiar JSON para programas",
    "save": "Guardar resultados",
    "open_folder": "Abrir carpeta de resultados",
    "cancel": "Solicitar cancelación",
    "analyze": "Abrir validación tras compilar",
    "reset": "Limpiar entrada",
    "load_file": "Cargar archivo local",
    "paste": "Pegar desde el portapapeles",
    "example": "Cargar ejemplo",
    "settings_reset": "Restablecer configuracion local",
    "settings": "Abrir configuracion",
    "help": "Abrir ayuda",
    "validation": "Ver validacion",
}


CONTEXT_HELP = {
    "Panel principal": (
        "Panel principal",
        "Que hace:\nResume el estado de la aplicacion y muestra accesos rapidos.\n\n"
        "Cuando conviene usarlo:\nAl abrir NPSC o despues de una compilacion para revisar estado, perfil y preservacion.",
    ),
    "Compilador": (
        "Compilador",
        "Que hace:\nPermite escribir tu prompt, elegir modelo y mejorar la peticion.\n\n"
        "Cuando conviene usarlo:\nEs el flujo principal. En modo sencillo basta con dejar AUTO y pulsar Mejorar prompt.",
    ),
    "Resultados": (
        "Resultados",
        "Qué hace:\nMuestra el prompt listo, el informe completo, la validación y, en modo avanzado, salidas técnicas.\n\n"
        "Para usar el resultado en otra IA, copia Prompt listo para usar.",
    ),
    "Validación": (
        "Validación",
        "Qué hace:\nExplica conservación del significado, advertencias y restricciones conservadas.\n\n"
        "Cuando conviene usarlo:\nRevísalo si el prompt es importante o si activas validación estricta.",
    ),
    "Perfiles": (
        "Perfiles semanticos",
        "Que hace:\nExplica AUTO, FAST, STANDARD, ADVANCED, ROP y RESEARCH_MAX.\n\n"
        "Cuando conviene usarlo:\nCuando quieras elegir manualmente el nivel de preservacion y estructura.",
    ),
    "Reglas y modelos": (
        "Reglas y modelos",
        "Qué hace:\nMuestra reglas semánticas seleccionadas y perfiles de modelo.\n\n"
        "Cuando conviene usarlo:\nEn modo avanzado, para auditar por qué se activaron ciertas instrucciones.",
    ),
    "Configuración": (
        "Configuracion",
        "Que hace:\nGestiona preferencias locales y permite restablecerlas.\n\n"
        "Advertencia:\nNo borra backups ni artefactos exportados.",
    ),
    "Ayuda": (
        "Ayuda",
        "Que hace:\nResume atajos y flujo de uso.\n\n"
        "Cuando conviene usarlo:\nSi necesitas recordar como mejorar, copiar o guardar resultados.",
    ),
    "Glosario": (
        "Glosario",
        "Qué hace:\nExplica palabras y abreviaturas de la aplicación en lenguaje sencillo.\n\n"
        "Cuando conviene usarlo:\nSi ves un término técnico y quieres entenderlo sin leer un manual completo.",
    ),
    "Acerca de": (
        "Acerca de",
        "Que hace:\nMuestra informacion de producto y privacidad.\n\n"
        "Advertencia:\nNPSC funciona localmente y no envia prompts a servidores externos.",
    ),
    "profile": (
        "Tipo de mejora",
        "Qué hace:\nControla cuánta estructura, preservación y revisión necesita tu prompt.\n\n"
        "Cuando conviene usarlo:\nDeja AUTO si no tienes claro qué opción escoger.",
    ),
    "target": (
        "Modelo destino",
        "Que hace:\nAdapta la forma del prompt al modelo donde lo pegaras.\n\n"
        "Cuando conviene usarlo:\nUsa AUTO o elige Codex, GPT, Claude, Hermes, custom u otro perfil disponible.",
    ),
    "level": (
        "Nivel de detalle técnico",
        "Qué hace:\nControla la densidad de la salida técnica. Conservador preserva más; Más compacto requiere revisión.\n\n"
        "Recomendación:\nUsa Automático según el tipo de mejora si no necesitas comparar niveles.",
    ),
    "strict": (
        "Validación estricta",
        "Qué hace:\nBloquea salidas con pérdida o riesgo crítico.\n\n"
        "Cuando conviene usarlo:\nPara prompts importantes, restricciones fuertes o tareas de alto riesgo.",
    ),
    "privacy": (
        "Privacidad",
        "Controla cuánto del prompt original se guarda en archivos técnicos.\n\n"
        "Guardar original completo ofrece más trazabilidad. Guardar solo huella digital protege más el contenido. Guardar vista parcial recortada queda en un punto intermedio.",
    ),
    "custom_model": (
        "Modelo custom",
        "Que hace:\nPermite registrar el nombre visible de un modelo no listado.\n\n"
        "Advertencia:\nNo inventa capacidades; solo documenta el destino y usa defaults seguros.",
    ),
    "advanced_mode": (
        "Modo avanzado",
        "Qué hace:\nMuestra NSL compacto, JSON para programas, reglas semánticas, restricciones, métricas y validación técnica.\n\n"
        "Cuando conviene usarlo:\nSi quieres auditar la salida o preparar integraciones.",
    ),
    "results_tab": (
        "Pestañas de resultados",
        "Qué hace:\nCada pestaña muestra una vista distinta del mismo resultado.\n\n"
        "Copia Prompt listo para usar. Consulta NSL o JSON solo si necesitas trazabilidad técnica.",
    ),
    "compact_nsl": (
        "NSL compacto",
        "Representación técnica resumida de intención, contexto, tareas, restricciones y salida esperada.\n\n"
        "Para uso normal copia Prompt listo para usar.",
    ),
    "json_programs": (
        "JSON para programas",
        "Archivo estructurado pensado para automatización, scripts o futuras integraciones.\n\n"
        "Normalmente no necesitas abrirlo ni copiarlo para usar tu prompt.",
    ),
    "semantic_rules": (
        "Reglas semánticas",
        "Criterios internos seleccionados para conservar intención, seguridad o estructura.\n\n"
        "Úsalas solo si necesitas auditar la salida.",
    ),
    "constraints_origin": (
        "Restricciones y origen",
        "Muestra condiciones detectadas y de dónde vienen.\n\n"
        "Sirve para comprobar que las reglas importantes del prompt se conservaron.",
    ),
    "complete_report": (
        "Informe completo",
        "Reúne prompt original permitido por privacidad, perfil aplicado, restricciones, métricas y trazabilidad.\n\n"
        "Nombre técnico: audit bundle.",
    ),
}


CONTEXT_GLOSSARY = {
    "profile": "semantic_profile",
    "level": "technical_detail_level",
    "privacy": "privacy",
    "strict": "strict_validation",
    "advanced_mode": "advanced_mode",
    "results_tab": "result",
    "compact_nsl": "compact_nsl",
    "json_programs": "json_for_programs",
    "semantic_rules": "semantic_rule",
    "constraints_origin": "constraints_origin",
    "complete_report": "audit_bundle",
}


def apply_tooltip(widget, key: str) -> None:
    widget.setToolTip(BRIEF_TOOLTIPS.get(key, ""))


def help_text(key: str) -> tuple[str, str]:
    return CONTEXT_HELP[key]


def glossary_term_for(key: str) -> str | None:
    return CONTEXT_GLOSSARY.get(key)
