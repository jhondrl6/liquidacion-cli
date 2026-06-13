

# **Reporte Legal-Técnico 2025: Especificación Normativa para el Cálculo Automatizado (CLI) de la Liquidación Laboral en Colombia**

### **I. Resumen Ejecutivo y Declaración Normativa**

Este informe establece el marco jurídico actualizado y la línea base técnica para el desarrollo de una herramienta de interfaz de línea de comandos (CLI) destinada a calcular la liquidación final de prestaciones sociales y finiquito de contratos laborales privados en Colombia, con referencia a la normatividad vigente hasta octubre de 2025\. La base del cálculo es el Código Sustantivo del Trabajo (CST), complementado por la Ley 50 de 1990 y las modificaciones introducidas por la **Ley 2466 de 2025** (Reforma Laboral). Se incorporan parámetros oficiales de 2025, incluyendo el Salario Mínimo Legal Mensual Vigente (SMMLV) de $1.423.500 1 y se aborda la complejidad de la Base Salarial de Liquidación (SBL), destacando la obligación de promediar el ingreso anual para Cesantías e Indemnización en casos de salario variable, conforme a la jurisprudencia más reciente.2 El CLI propuesto garantiza la transparencia al citar las fuentes legales en el resultado de la liquidación, y alerta sobre la crucial obligación de pago inmediato de finiquito (Art. 65 CST).

### **II. Fundamento Normativo de la Liquidación Laboral en Colombia**

#### **A. Alcance y Requisitos de Aplicación**

La liquidación laboral es el pago final de las obligaciones pendientes que el empleador debe realizar al trabajador al terminar la relación de trabajo. Su procedencia está estrictamente ligada a la existencia de un contrato de trabajo, ya sea escrito o verbal, donde primen la subordinación y el servicio personal remunerado (Art. 22-24 CST).

El diseño del script CLI debe integrar validaciones que confirmen la naturaleza de la relación laboral. Es fundamental que el sistema **rechace** el cálculo si se trata de un contrato de prestación de servicios (CPS). La ley colombiana establece que los contratistas de servicios no son sujetos de prestaciones sociales (prima, cesantías, vacaciones, indemnización por despido) ni están obligados a cotizar a la seguridad social bajo el régimen de dependencia, sino que deben asumir sus propios costos como independientes.3

Además, la existencia de una relación laboral implica la obligación patronal de afiliación y pago oportuno de los aportes al Sistema de Seguridad Social Integral (Salud, Pensión y Riesgos Laborales) hasta el último día laborado.4 El incumplimiento de esta obligación no solo genera sanciones administrativas y penales, sino que, en materia de riesgos laborales, obliga al empleador a asumir directamente las prestaciones que el sistema no cubra por falta de cotización.5

#### **B. Requisitos Formales de Terminación y Plazo de Pago**

El finiquito de la relación laboral debe realizarse con total diligencia.

1. **Plazo Inmediato (Art. 65 CST):** La norma más crítica para el CLI es el plazo de pago. El Código Sustantivo del Trabajo (CST) exige que el pago total de salarios y prestaciones sociales adeudadas debe efectuarse **al momento mismo de la terminación del contrato**.7 La Corte Constitucional y la Función Pública han insistido en la necesidad de la máxima diligencia para evitar perjuicios al mínimo vital del trabajador, si bien la jurisprudencia administrativa a veces contempla un plazo "moderado" en el sector público, el rigor en el sector privado es inmediato.8 Por lo tanto, el CLI debe establecer la fecha\_retiro como la fecha\_limite\_pago\_legal.  
2. **Sanción Moratoria:** Si el empleador incumple la obligación de pago inmediato sin que medie buena fe demostrada, se activa la sanción moratoria prevista en el Artículo 65 del CST. Esta sanción implica el pago de **un día de salario por cada día de retardo**.9 La base de la sanción es el salario devengado por el trabajador.  
3. **Renunciabilidad:** El trabajador que recibe su liquidación y firma un documento de "paz y salvo" no pierde el derecho a reclamar judicialmente si el cálculo fue incorrecto o si existen derechos irrenunciables pendientes.10 El CLI se enfoca en calcular el valor legalmente debido, no en un valor negociable.

#### **C. Tabla de Fuentes Legales Clave (Actualizada a Octubre 2025\)**

La siguiente tabla resume las bases legales citables en la salida JSON del CLI para sustentar cada componente:

Tabla de Fuentes Legales de la Liquidación Laboral (Octubre 2025\)

| Componente Regulado | Fuente Legal Principal | Artículo/Norma Específica | Vigencia/Relevancia |
| :---- | :---- | :---- | :---- |
| Contrato de Trabajo | Código Sustantivo del Trabajo (CST) | Art. 22-24, 46, 64 | Base de la relación laboral y tipología de contratos. |
| Cesantías | CST / Ley 50 de 1990 | Arts. 249-252 CST; Art. 99 L. 50/90 | Régimen de liquidación anual y consignación. \[11\] |
| Intereses sobre Cesantías | Ley 50 de 1990 | Art. 99 | Tasa anual del 12%. \[12\] |
| Prima de Servicios | CST | Arts. 306-308 | Pago semestral obligatorio. \[11\] |
| Vacaciones No Disfrutadas | CST | Arts. 186-192 | Compensación en dinero. \[11\] |
| Compensación Vacaciones (Acuerdo) | CST | Art. 189 | Acuerdo escrito, máx 50%, solicitud del trabajador. |
| Indemnización (Indefinido) | CST | Art. 64 | Tablas de factores según el salario (doble tabla). \[13\] |
| Indemnización (SBL Variable) | Jurisprudencia CSJ | Radicado SL1659-2025 (Marzo 2025\) | Define la aplicación del promedio anual para la SBL de la indemnización en salarios variables. \[2, 14\] |
| Auxilio de Transporte | Ley 15/59, Decreto 1573/24 | Dec. 1573/24 | Fija valor 2025 ($200.000) y criterio de aplicabilidad. 15 |
| Recargos y Jornada | CST / Ley 2466 de 2025 | Arts. 160, 179 CST; Art. 14 L. 2466/25 | Modifica recargo dominical (80% desde Jul 1/25) y jornada nocturna (7 PM desde Dic 25/25). |
| Sanción Moratoria (Finiquito) | CST | Art. 65, Inciso 1° | Pago de 1 día de salario por día de retardo. 7 |
| Sanción Moratoria (Cesantías) | Ley 50 de 1990 | Art. 99, Num. 3 | Pago de 1 día de salario por día de retardo de la consignación. |

### **III. Determinación de la Base Salarial de Liquidación (SBL)**

La correcta definición de la Base Salarial de Liquidación (SBL) es el aspecto técnico más crucial y complejo, ya que varía según la prestación y la naturaleza del salario (fijo o variable).

#### **A. Componentes de la SBL General**

La SBL general es la base para calcular Cesantías, Intereses sobre Cesantías y Prima de Servicios. Incluye todos los pagos que el trabajador recibe como retribución directa por su servicio, sean fijos u ocasionales. Esto abarca el salario base, las comisiones, las bonificaciones salariales, las horas extras, los recargos nocturnos, dominicales y festivos.17 Los pagos que no constituyen salario, como los viáticos ocasionales o las sumas pagadas por mera liberalidad o para desempeñar funciones (si están pactados como no salariales), se excluyen.

#### **B. Tratamiento del Auxilio de Transporte y Conectividad**

El Auxilio de Transporte, fijado en $200.000 mensuales para 2025 15, se suma a la SBL General (Cesantías y Prima) si el trabajador devenga hasta dos (2) SMMLV ($2.847.000 en 2025).18

Sin embargo, existe una excepción fundamental que el CLI debe validar: el auxilio de transporte solo se causa si el trabajador incurre efectivamente en gastos de traslado de su casa al trabajo. Si, como se plantea en el caso de un trabajador rural, este **reside en el lugar de trabajo** (finca o predio), **no tiene derecho** al reconocimiento y pago del auxilio, incluso si su salario es inferior a los 2 SMMLV.19 Esta validación prioritaria debe ser incluida en el *script* mediante el parámetro de entrada auxilio\_aplica.

#### **C. Manejo de Salarios Variables y la Novedad Jurisprudencial 2025**

Cuando el trabajador devenga un salario variable (ejemplo: alto porcentaje en comisiones), la liquidación debe basarse en el promedio.

1. **SBL para Cesantías y Prima:**  
   * Para **Cesantías**, se utiliza el promedio de lo devengado en el último año de servicio, o de todo el tiempo si este fuera inferior a un año (Art. 253 Num. 1 CST).20  
   * Para **Prima**, se utiliza el promedio de lo devengado durante el semestre a liquidar.20  
2. **SBL para Indemnización por Despido sin Justa Causa:** El Artículo 64 del CST, al referirse al cálculo de la indemnización, simplemente menciona "salario", lo cual históricamente generaba un vacío cuando este era variable. Una reciente jurisprudencia de la Corte Suprema de Justicia (Radicado SL1659-2025, de marzo de 2025\) ha resuelto esta ambigüedad. La Corte determinó que, para garantizar una reparación equitativa, la SBL para calcular la indemnización debe fijarse tomando el promedio de lo devengado durante el año inmediatamente anterior al despido. El CLI, por lo tanto, debe aplicar la misma regla del promedio anual que se usa para Cesantías, garantizando que el parámetro de entrada pagos\_variables\_12\_meses se utilice para establecer el SBL\_GENERAL que se usará en la liquidación de la indemnización.

#### **D. Base Salarial Específica para Vacaciones Compensadas**

La base salarial para la liquidación de las vacaciones compensadas es taxativa y excluyente (Art. 192 CST). Para el cálculo de la compensación en dinero de las vacaciones no disfrutadas, se debe excluir de la SBL: el auxilio de transporte, las horas extras y los recargos por trabajo nocturno, dominical o festivo.6 El CLI debe calcular una SBL\_VACACIONES distinta a la SBL\_GENERAL.

#### **D.1. Compensación Parcial de Vacaciones en Dinero (Liquidación Periódica)**

El Artículo 189 del CST (modificado por el Art. 14 de la Ley 1429 de 2010) faculta a empleador y trabajador para acordar por escrito, previa solicitud del trabajador, el pago en dinero de hasta la mitad de las vacaciones.

*   **Requisitos de Validez:**
    1.  **Solicitud del Trabajador:** Debe mediar petición del empleado.
    2.  **Acuerdo Escrito:** El pacto debe constar por escrito (Soporte documental obligatorio).
    3.  **Límite Legal:** Máximo el 50% de los días causados.
    4.  **Disfrute Obligatorio:** Los días restantes deben ser descansados efectivamente.

En el contexto del CLI, esta figura permite que en una **Liquidación Periódica** se incluya un pago por concepto de vacaciones compensadas, siempre que se valide el límite del 50% y se genere la cláusula de acuerdo en el comprobante de pago.

### **VI. Cálculo de la Indemnización por Terminación Unilateral sin Justa Causa (Art. 64 CST)**

### **IV. Parámetros Oficiales 2025 y Hitos Normativos**

#### **A. Parámetros Monetarios Fijos (Hard-Code para CLI)**

La implementación del CLI requiere la parametrización de los siguientes valores decretados y vigentes a partir del 1 de enero de 2025:

Parámetros Oficiales Monetarios 2025

| Concepto | Valor Mensual 2025 (COP) | Dato Base para CLI | Referencia Normativa |
| :---- | :---- | :---- | :---- |
| Salario Mínimo Mensual Legal Vigente (SMMLV) | $1.423.500 | SMMLV\_2025 | Presidencia |
| Auxilio de Transporte/Conectividad | $200.000 | AUXILIO\_TRANS\_2025 | Decreto 1573 de 2024 |
| Límite Salarial para Auxilio (2 SMMLV) | $2.847.000 | LIMITE\_AUXILIO | CST (Implícito) 18 |
| Tope Máximo IBC Seguridad Social | $\\sim$ $64.057.500 | TOPE\_IBC\_SS\_2025 | 45 SMMLV (UGPP/CMS) |

#### **B. Implicaciones de la Ley 2466 de 2025 (Reforma Laboral)**

La Ley 2466 de 2025 establece cambios relevantes en los recargos y horarios que son críticos para liquidar correctamente el salario pendiente y las horas extras devengadas en el periodo final. La reforma establece una aplicación escalonada.

1. **Recargo Dominical y Festivo (Art. 179 CST modificado):** El factor de recargo dominical pasa del 75% al 80% a partir del **1 de julio de 2025**. Si la liquidación abarca días trabajados en domingo o festivo entre el 1 de julio y el 15 de octubre de 2025, el CLI debe aplicar el factor del 80%. El recargo nocturno dominical pasa a ser del 115% (35% nocturno \+ 80% dominical) a partir de esa misma fecha.  
2. **Jornada Nocturna (Art. 160 CST modificado):** El horario de la jornada nocturna se modificará para iniciar a las 7:00 p.m. y terminar a las 6:00 a.m., pero este cambio solo entrará en vigencia a partir del **25 de diciembre de 2025**. Dado que la liquidación se proyecta hasta octubre de 2025, el horario nocturno aplicable es el que inicia a las 9:00 p.m.21

El *script* requiere una validación de la fecha de servicio para aplicar la tarifa del recargo dominical correcta.

### **V. Liquidación y Fórmulas Detalladas de Prestaciones Sociales y Finiquito**

El cálculo de las prestaciones se basa en el año de 360 días (30 días por mes).

#### **A. Salario Pendiente y Horas Extras**

Incluye el salario ordinario correspondiente a los días laborados en el mes de retiro (días\_saldo\_salario) y cualquier recargo u hora extra devengada y no pagada.

* **Fórmula Base:** Salario Pendiente \= $SBL\_{Diario} \\times Días\_{Saldo}$.  
* **Recargos:** Se calcularán sobre el valor de la hora ordinaria, aplicando el 35% por nocturno y, si aplica después del 1 de julio de 2025, el 80% por dominical o festivo.  
* **Sustento Legal:** Art. 161, 167 CST.

#### **B. Cesantías (Liquidación Periódica Anual o Fracción Final)**

Se calculan sobre el periodo (anual o fracción), utilizando la SBL General.

* **Periodo de Liquidación Anual (Corte 31 Dic):** La liquidación es anual. La **consignación** debe realizarse antes del 14 de febrero del año siguiente. 7  
* **SBL a Utilizar:** SBL General (promedio anual si es variable).20  
* **Fórmula Legal:** $C \= (SBL \\times Días\_{Trabajados}) / 360$.  
* **Sustento Legal:** Art. 249 CST, Art. 99 L. 50/90.

#### **C. Intereses sobre Cesantías**

Se calculan sobre el valor de las Cesantías causadas en el periodo (anual o final), a una tasa fija del 12% anual.

* **Plazo de Pago:** El pago es directo al trabajador antes del 31 de enero del año siguiente.3  
* **Tasa Legal:** 12% anual (0.12).  
* **Fórmula Legal:** $I \= (C \\times Días\_{Trabajados} \\times 0.12) / 360$.  
* **Sustento Legal:** Art. 99 Ley 50/90.

#### **D. Prima de Servicios (Fracción Semestre)**

Se paga la fracción del semestre en curso.

* **Plazo de Pago:** La prima es semestral (antes del 30 de junio y antes del 20 de diciembre).  
* **SBL a Utilizar:** SBL General (promedio semestral si es variable).20  
* **Fórmula Legal:** $P \= (SBL \\times Días\_{Semestre}) / 360$.  
* **Sustento Legal:** Art. 306 CST.

#### **E. Vacaciones Compensadas No Disfrutadas (Solo Finiquito)**

Solo aplica a la terminación del contrato (Finiquito). Se utiliza una base más restrictiva (SBL Vacaciones).

* **SBL a Utilizar:** SBL Vacaciones (excluye Auxilio, Extras y Recargos).6  
* **Fórmula Legal:** $V \= (SBL\_{Vacaciones} \\times Días\_{Trabajados\\\_Acumulados}) / 720$.22  
* **Sustento Legal:** Art. 186-192 CST.

### **VI. Cálculo de la Indemnización por Terminación Unilateral sin Justa Causa (Art. 64 CST)**

**Aplica exclusivamente al modo Finiquito.**

#### **A. Contratos a Término Indefinido**

El cálculo de la indemnización se realiza utilizando la SBL Diario (promedio anual si el salario es variable, según la CSJ 2025 ). La ley establece una tabla de factores (doble tabla) basada en si el salario del trabajador excede o no los 10 SMMLV ($14.235.000 en 2025).

| Rango Salarial | Servicio ≤ 1 Año | Servicio \> 1 Año (Días Adicionales) | Sustento Legal |
| :---- | :---- | :---- | :---- |
| Salario \< 10 SMMLV | 30 días de salario | 20 días por cada año subsiguiente y proporcional por fracción | Art. 64, lit. a) CST |
| Salario $\\ge$ 10 SMMLV | 20 días de salario | 15 días por cada año subsiguiente y proporcional por fracción | Art. 64, lit. b) CST |

#### **B. Contratos a Término Fijo o por Obra/Labor**

* **Término Fijo:** Igual al valor de los salarios que falten para el cumplimiento del plazo pactado.  
* **Obra o Labor:** Equivalente a los salarios que falten para la terminación de la obra, **no inferior a quince (15) días** de salario.

### **VII. Especificación de la Línea Base Técnica (CLI Script Implementation)**

El pseudocódigo incorpora el modo de liquidación (PERIÓDICA o FINIQUITO) para adaptar la lógica de cálculo y la salida.

#### **Pseudocódigo de la Función Central liquidar\_colombia()**

Python

\# Definición de Parámetros Fijos (Hard-Codes 2025\)  
SMMLV\_2025 \= 1423500.0  
AUXILIO\_TRANS\_2025 \= 200000.0  
LIMITE\_AUXILIO \= 2 \* SMMLV\_2025  
TASA\_INT\_CESANTIAS \= 0.12  
DIAS\_ANUALES \= 360.0 \# Base legal para prestaciones  
RECARGO\_DOMINICAL\_FACTOR\_2025 \= 0.80 \# Vigente desde Jul 1, 2025 

def liquidar\_colombia(fecha\_ingreso, fecha\_retiro, modo\_liquidacion, tipo\_contrato,   
                      motivo\_terminacion, salario\_base\_fijo\_mensual,   
                      pagos\_variables\_12\_meses, dias\_vacaciones\_pendientes,   
                      auxilio\_aplica, dias\_saldo\_salario, salario\_pendiente\_recargos=0.0):  
      
    \# 1\. CÁLCULO DE TIEMPO Y BASES SALARIALES  
      
    \# En modo PERIÓDICA, la fecha de retiro actúa como fecha de corte para el cálculo.  
    fecha\_corte\_liquidacion \= fecha\_retiro   
    DIAS\_SERVICIO \= calcular\_dias(fecha\_ingreso, fecha\_corte\_liquidacion)  
    AÑOS\_FRACCION \= DIAS\_SERVICIO / DIAS\_ANUALES 

    \# Determinación de SBL... (misma lógica que en versión anterior)

    \# 2\. AJUSTE POR AUXILIO DE TRANSPORTE  
    APLICA\_AUXILIO \= auxilio\_aplica and (SBL\_FIJO \< LIMITE\_AUXILIO)   
      
    \#... Lógica de cálculo de Auxilio...  
          
    SBL\_DIARIO \= SBL\_GENERAL / 30.0

    \# 3\. CÁLCULO DE PRESTACIONES  
    LIQUIDACION \= {}

    \# 3.1. Salario Pendiente (Solo Finiquito)  
    if modo\_liquidacion \== "FINIQUITO":  
        \#... Lógica de cálculo de Salario Pendiente...  
        LIQUIDACION \= SALARIO\_ORDINARIO\_PENDIENTE \+ salario\_pendiente\_recargos   
    else:  
        LIQUIDACION \= 0.0  
      
    \# 3.2. Cesantías (Periodo de Ingreso a Fecha de Corte)  
    DIAS\_CESANTIAS \= DIAS\_SERVICIO  
    CESANTIAS \= (SBL\_GENERAL \* DIAS\_CESANTIAS) / DIAS\_ANUALES  
    LIQUIDACION\['Cesantias'\] \= CESANTIAS  
      
    \# 3.3. Intereses sobre Cesantías  
    INTERESES\_CESANTIAS \= (CESANTIAS \* DIAS\_CESANTIAS \* TASA\_INT\_CESANTIAS) / DIAS\_ANUALES  
    LIQUIDACION\['Intereses\_Cesantias'\] \= INTERESES\_CESANTIAS

    \# 3.4. Prima de Servicios (Fracción del Semestre en curso)  
    DIAS\_PRIMA \= calcular\_dias\_semestre\_curso(fecha\_corte\_liquidacion)  
    PRIMA \= (SBL\_PRIMA \* DIAS\_PRIMA) / DIAS\_ANUALES  
    LIQUIDACION\['Prima'\] \= PRIMA

    \# 3.5. Vacaciones Compensadas (Solo Finiquito)  
    INDEMNIZACION \= 0.0  
    if modo\_liquidacion \== "FINIQUITO":  
        \#... Lógica de cálculo de Vacaciones Compensadas...  
        LIQUIDACION\['Vacaciones'\] \= VACACIONES\_TOTAL  
      
    \# 4\. CÁLCULO DE INDEMNIZACIÓN (Solo Finiquito)  
    rango\_salarial \= "No aplica"  
    if modo\_liquidacion \== "FINIQUITO" and motivo\_terminacion \== "Sin\_Justa\_Causa":  
        \#... Lógica de cálculo de Indemnización Art. 64 CST...  
        INDEMNIZACION \= calcular\_indemnizacion\_art64(SBL\_GENERAL, DIAS\_SERVICIO, tipo\_contrato, SMMLV\_2025)  
        LIQUIDACION\['Indemnizacion'\] \= INDEMNIZACION  
      
    \# 5\. RESULTADO Y GENERACIÓN DE DOCUMENTOS  
    TOTAL\_FINAL \= sum(LIQUIDACION.values())  
      
    return generar\_json\_output(TOTAL\_FINAL, fecha\_corte\_liquidacion, LIQUIDACION, rango\_salarial, alerta\_aux, modo\_liquidacion)

#### **D. Notas de Implementación Técnica (Actualizadas)**

1. **Manejo de Modos de Liquidación:** El parámetro modo\_liquidacion debe definir si se calcula un **Finiquito** (incluye Salario Pendiente, Vacaciones e Indemnización potencial, con plazo de pago inmediato Art. 65 CST) o una liquidación **Periódica**. En modo PERIÓDICA, la fecha\_retiro funciona como fecha de corte para el cálculo de las prestaciones causadas, y se omite el cálculo de Indemnización y Vacaciones Compensadas.  
2. **Validación de Fechas Críticas:** El script debe validar la fecha de prestación de servicio para aplicar el factor correcto del recargo dominical (75% antes del 1 de julio de 2025; 80% desde el 1 de julio de 2025).  
3. **Modelo de Soporte Legal:** El CLI debe generar un documento imprimible (adicional al JSON) que sirva como **Comprobante de Pago Periódico**, detallando la base, el periodo liquidado y los plazos de consignación (Cesantías: 14 Feb; Intereses: 31 Ene), crucial para la prueba ante el Ministerio del Trabajo.

### **VIII. Ejemplo de Ejecución Detallado (Caso Práctico 2025: Liquidación Periódica)**

El ejemplo simula el caso de una **Liquidación Periódica Anual** (Corte 15 de Noviembre) para un trabajador con salario fijo que reside en la finca, liquidando las prestaciones causadas en ese periodo de 360 días.

**Parámetros del Caso (Corte Periódico 2025):**

| Parámetro de Entrada | Valor | Nota de Validación |
| :---- | :---- | :---- |
| Fecha de Ingreso | 2024-11-16 |  |
| Fecha de Retiro (Corte) | 2025-11-15 | Período solicitado de 360 días. |
| Modo de Liquidación | PERIÓDICA | Excluye Indemnización y Salario Pendiente. |
| Salario Fijo Mensual (SBL) | $2.000.000 | \< 2 SMMLV ($2.847.000). |
| Residencia en el lugar de trabajo | Sí | Implica auxilio\_aplica \= False.19 |
| Días Salario Pendiente | 0 | No aplica en liquidación periódica. |

**Desglose de la Liquidación Periódica (360 días):**

| Concepto | Cálculo Detallado | Valor Liquidado (COP) | Sustento Legal |
| :---- | :---- | :---- | :---- |
| **1\. Cesantías** | ($2.000.000 $\\times$ 360\) / 360 | $2.000.000 | Art. 249 CST |
| **2\. Intereses sobre Cesantías** | ($2.000.000 $\\times$ 360 $\\times$ 0.12) / 360 | $240.000 | Art. 99 Ley 50/90 |
| **3\. Prima de Servicios (2° Semestre: 1 Jul \- 15 Nov)** | Días a liquidar: 138 días. ($2.000.000 $\\times$ 138\) / 360 | $766.667 | Art. 306 CST |
| **TOTAL OBLIGACIONES PERIÓDICAS** | Sumatoria (1 a 3\) | **$3.006.667** |  |

**A. Salida JSON (Fragmento):**

JSON

{  
  "parametros\_calculo": {  
    "modo\_liquidacion": "PERIÓDICA",  
    "fecha\_corte": "2025-11-15",  
    "SBL\_General": 2000000.0,  
    "tiempo\_servicio\_dias\_periodo": 360  
  },  
  "total\_liquidacion\_periodica": 3006667.0,  
  "detalles\_prestaciones": {  
    "Cesantias": {  
      "valor": 2000000.0,  
      "dias\_liquidados": 360,  
      "sustento\_legal": "Art. 249 CST",  
      "plazo\_pago\_legal": "Consignación antes de 2026-02-14. (Sanción moratoria Art. 99 L. 50/90)"  
    },  
    "Intereses\_Cesantias": {  
      "valor": 240000.0,  
      "dias\_liquidados": 360,  
      "sustento\_legal": "Art. 99 Ley 50/90",  
      "plazo\_pago\_legal": "Pago Directo antes de 2026-01-31. "  
    },  
    "Prima": {  
      "valor": 766667.0,  
      "dias\_liquidados": 138,  
      "sustento\_legal": "Art. 306 CST",  
      "plazo\_pago\_legal": "Pago Directo antes de 2025-12-20. "  
    },  
    "Salario\_Pendiente": {  
      "valor": 0.0,  
      "nota": "No aplica en modo PERIÓDICA"  
    }  
  },  
  "validaciones\_y\_alertas": {  
    "alerta\_auxilio\_transporte": "Auxilio de transporte excluido. Motivo: Residencia en sitio de trabajo (Finca Rural). ",  
    "nota\_general": "Este cálculo corresponde a la liquidación periódica de prestaciones causadas y no a un finiquito de contrato."  
  }  
}

**B. Modelo de Formato de Liquidación Periódica (Soporte de Pago)**

Este documento debe ser generado por el CLI y firmado por ambas partes para soportar el cumplimiento de las obligaciones de pago directo (Intereses sobre Cesantías y Prima de Servicios), y la notificación de la consignación (Cesantías).

---

## **COMPROBANTE DE LIQUIDACIÓN PERIÓDICA DE PRESTACIONES SOCIALES**

### **(Período de Causación Anual \- No Finiquito)**

Fecha de Generación: 2025-11-16  
Empresa:  
NIT:

| DATOS DEL TRABAJADOR | VALOR |
| :---- | :---- |
| Nombre Completo |  |
| Cédula de Ciudadanía |  |
| Fecha de Ingreso | 2024-11-16 |
| Fecha de Corte de Liquidación | 2025-11-15 |
| Salario Base Mensual | $2.000.000 |

---

### **DESGLOSE DE PRESTACIONES SOCIALES CAUSADAS**

Período liquidado: 360 días (Noviembre 16 de 2024 a Noviembre 15 de 2025\)  
Base de Liquidación (SBL): $2.000.000 (Auxilio de Transporte excluido por excepción legal 19\)  
Total Bruto Causado: $3.006.667

| CONCEPTO | VALOR A PAGAR/CONSIGNAR (COP) | PERÍODO / DÍAS | PLAZO LEGAL |
| :---- | :---- | :---- | :---- |
| **1\. Cesantías** | $2.000.000 | 360 días | **Consignación** antes del 14/02/2026 7 |
| **2\. Intereses sobre Cesantías** | $240.000 | 360 días (12% anual) | **Pago Directo** antes del 31/01/2026 3 |
| **3\. Prima de Servicios (2° Semestre)** | $766.667 | 138 días | **Pago Directo** antes del 20/12/2025 |

---

### **DECLARACIÓN DE RECIBO Y CONSIGNACIÓN**

Yo,, identificado(a) con C.C., declaro que:

1. Recibo en este acto la suma de **$1.006.667 COP** (Un Millón Seis Mil Seiscientos Sesenta y Siete Pesos Colombianos) correspondiente al pago directo de:  
   * Intereses sobre Cesantías: $240.000.  
   * Prima de Servicios (2° Semestre): $766.667.  
2. Quedo notificado de la obligación del empleador de consignar el valor de las Cesantías (Concepto 1\) en el Fondo de Cesantías antes del 14 de febrero de 2026, conforme al artículo 99 de la Ley 50 de 1990\.

Con la firma de este comprobante, se verifica el pago de las sumas aquí estipuladas y la notificación de la consignación.

**El trabajador, mediante este documento, no renuncia a reclamar judicialmente cualquier diferencia o error en el cálculo que la ley garantice como irrenunciable.**

| \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| :---- | :---- |
| **Firma del Empleador (o Representante Legal)** | **Firma del Trabajador** |
| **C.C./C.E.** | **C.C./C.E.** |

#### ---

**Obras citadas**

1. El salario mínimo para 2025 aumentó en 9,5% y quedará en $1'423.500, fecha de acceso: octubre 20, 2025, [https://www.presidencia.gov.co/prensa/Paginas/El-salario-minimo-para-2025-aumentara-el-9-54-porciento-y-queda-en-1423500-presidente-Gustavo-Petro-241224.aspx](https://www.presidencia.gov.co/prensa/Paginas/El-salario-minimo-para-2025-aumentara-el-9-54-porciento-y-queda-en-1423500-presidente-Gustavo-Petro-241224.aspx)  
2. CÁLCULO DE LA INDEMNIZACIÓN EN EL SALARIO VARIABLE \- Scola Abogados, fecha de acceso: octubre 20, 2025, [https://scolalegal.com/calculo-de-la-indemnizacion-en-el-salario-variable/](https://scolalegal.com/calculo-de-la-indemnizacion-en-el-salario-variable/)  
3. fecha de acceso: octubre 20, 2025, [https://www.magneto365.com/co/blog/diferencias-contrato-laboral-prestacion-servicios\#:\~:text=En%20el%20contrato%20laboral%2C%20el%20trabajador%20recibe%20prestaciones%20sociales%2C%20seguridad,propios%20costos%20de%20seguridad%20social.](https://www.magneto365.com/co/blog/diferencias-contrato-laboral-prestacion-servicios#:~:text=En%20el%20contrato%20laboral%2C%20el%20trabajador%20recibe%20prestaciones%20sociales%2C%20seguridad,propios%20costos%20de%20seguridad%20social.)  
4. ¿Qué hacer si no se afilia o paga la seguridad social del trabajador?, fecha de acceso: octubre 20, 2025, [https://www.minjusticia.gov.co/programas-co/LegalApp/Paginas/Que-hacer-si-no-se-afilia-o-paga-la-seguridad-social-del-trabajador.aspx](https://www.minjusticia.gov.co/programas-co/LegalApp/Paginas/Que-hacer-si-no-se-afilia-o-paga-la-seguridad-social-del-trabajador.aspx)  
5. Leyes desde 1992 \- Vigencia expresa y control de constitucionalidad \[DECRETO\_1295\_1994\_PR002\], fecha de acceso: octubre 20, 2025, [http://www.secretariasenado.gov.co/senado/basedoc/decreto\_1295\_1994\_pr002.html](http://www.secretariasenado.gov.co/senado/basedoc/decreto_1295_1994_pr002.html)  
6. I. ANTECEDENTES \- Corte Constitucional, fecha de acceso: octubre 20, 2025, [https://www.corteconstitucional.gov.co/relatoria/2002/t-503-02.htm](https://www.corteconstitucional.gov.co/relatoria/2002/t-503-02.htm)  
7. ¿En cuánto tiempo me deben pagar la liquidación? \- Firma de Abogados en Medellin, fecha de acceso: octubre 20, 2025, [https://derechoequidad.com/blog/en-cuanto-tiempo-me-deben-pagar-la-liquidacion/](https://derechoequidad.com/blog/en-cuanto-tiempo-me-deben-pagar-la-liquidacion/)  
8. Concepto 095021 de 2023 Departamento Administrativo de la Función Pública \- Gestor Normativo, fecha de acceso: octubre 20, 2025, [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=209288](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=209288)  
9. SANCIÓN MORATORIA \- La imposición de esta, no tienen aplicación automática, en atención a que la buena fe demostrada, fecha de acceso: octubre 20, 2025, [https://tribunalmedellin.com/images/decisiones/laboral/2023/05001310501520170098701.pdf](https://tribunalmedellin.com/images/decisiones/laboral/2023/05001310501520170098701.pdf)  
10. ¿Cómo liquidar un contrato de trabajo? \- Ministerio de Justicia y del Derecho, fecha de acceso: octubre 20, 2025, [https://www.minjusticia.gov.co/programas-co/LegalApp/Paginas/Como-liquidar-un-contrato-de-trabajo.aspx](https://www.minjusticia.gov.co/programas-co/LegalApp/Paginas/Como-liquidar-un-contrato-de-trabajo.aspx)  
11. Prestaciones sociales: ventajas de su cumplimiento para la empresa | FNA, fecha de acceso: octubre 20, 2025, [https://www.fna.gov.co/Blog/Paginas/Prestaciones-sociales-ventajas-de-su-cumplimiento-para-la-empresa.aspx](https://www.fna.gov.co/Blog/Paginas/Prestaciones-sociales-ventajas-de-su-cumplimiento-para-la-empresa.aspx)  
12. Auxilio de transporte 2025 en Colombia: valor y requisitos \- Treinta, fecha de acceso: octubre 20, 2025, [https://www.treinta.co/blog/auxilio-de-transporte-en-colombia-2025-valor-requisitos-y-como-aplicarlo-en-la-nomina](https://www.treinta.co/blog/auxilio-de-transporte-en-colombia-2025-valor-requisitos-y-como-aplicarlo-en-la-nomina)  
13. Decreto 1573 de 2024 \- Gestor Normativo \- Función Pública, fecha de acceso: octubre 20, 2025, [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=256836](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=256836)  
14. Cómo liquidar prestaciones sociales \- Siigo.com, fecha de acceso: octubre 20, 2025, [https://www.siigo.com/blog/liquidar-prestaciones-sociales/](https://www.siigo.com/blog/liquidar-prestaciones-sociales/)  
15. ¿Cuánto es el salario mínimo para el 2025 y cómo calcularlo? \- Cafam, fecha de acceso: octubre 20, 2025, [https://www.cafam.com.co/noticias/salario-minimo-2025](https://www.cafam.com.co/noticias/salario-minimo-2025)  
16. Concepto 169261 de 2023 Departamento Administrativo de la Función Pública \- Gestor Normativo, fecha de acceso: octubre 20, 2025, [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=220076](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=220076)  
17. REPÚBLICA DE COLOMBIA RAMA JUDICIAL TRIBUNAL SUPERIOR DEL DISTRITO JUDICIAL DE BUGA SALA SEGUNDA DE DECISIÓN LABORAL, fecha de acceso: octubre 20, 2025, [https://portalhistorico.ramajudicial.gov.co/documents/8695863/140909457/15SentenciaDescongestion2020-00269.pdf/f7a54e67-d205-4d72-b568-36b1a2ea6c2d](https://portalhistorico.ramajudicial.gov.co/documents/8695863/140909457/15SentenciaDescongestion2020-00269.pdf/f7a54e67-d205-4d72-b568-36b1a2ea6c2d)  
18. ¿Qué es el auxilio de transporte y qué hacer si no se reconoce o paga?, fecha de acceso: octubre 20, 2025, [https://www.minjusticia.gov.co/programas-co/LegalApp/Paginas/Que-es-el-auxilio-de-transporte-y-que-hacer-si-no-se-reconoce-o-paga.aspx](https://www.minjusticia.gov.co/programas-co/LegalApp/Paginas/Que-es-el-auxilio-de-transporte-y-que-hacer-si-no-se-reconoce-o-paga.aspx)  
19. Recargo dominical y nocturno: ¿Cómo liquidarlos 2025?, fecha de acceso: octubre 20, 2025, [https://recursos.bitakora.co/blog/recargo-nocturno-y-dominical-que-son-y-como-liquidarlos/](https://recursos.bitakora.co/blog/recargo-nocturno-y-dominical-que-son-y-como-liquidarlos/)