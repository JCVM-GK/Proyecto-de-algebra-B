# Proyecto-de-algebra-B

¿Qué hace este proyecto?

Es un Simulador Interactivo de Impedancia para circuitos RLC en serie. Permite visualizar en el plano complejo cómo se comporta la oposición al paso de la corriente alterna en función de la resistencia (R), inductancia (L), capacitancia (C) y la frecuencia de la fuente (f).

¿Cómo lo hace? (El motor matemático)

El simulador utiliza aritmética de números complejos para calcular la Impedancia Total ($Z$). La lógica se basa en las siguientes fórmulas:

Resistencia: Zr = R + 0j

Inducto: Zl = 0 + (2π fL)j (La oposición crece con la frecuencia)

Capacitor: Zc = 0 - (<img width="47" height="39" alt="image" src="https://github.com/user-attachments/assets/87ba3b8c-532c-4d3f-b407-d120bd01db3c" />
)j (La oposición decrece con la frecuencia).

Impedancia Total: Z {total} = Zr + Zl + Zc 
El programa convierte el resultado de forma rectangular (a + bj) a forma polar (magnitud y fase) para facilitar la lectura técnica:

Magnitud: |Z| = <img width="75" height="24" alt="image" src="https://github.com/user-attachments/assets/4fc847a7-6085-4529-952d-e97a37aca667" />

Fase: <img width="80" height="39" alt="image" src="https://github.com/user-attachments/assets/7c30c8d5-def7-4021-ad84-7d0634a09e94" />

Tecnologías utilizadas
Python 3.14+: Lenguaje base por su alta legibilidad y manejo nativo de flujos

Pygame-ce: Motor gráfico optimizado para el renderizado en tiempo real de los vectores y la interfaz interactiva

Matemática de Fasores: Implementación manual de una clase Complejo para entender la lógica desde cero (heredada de la arquitectura original en C++).
