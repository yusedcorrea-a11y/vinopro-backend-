# Ofuscación R8/ProGuard y mapping para Google Play

Cuando Google revisa y publica tu app, el build de **release** suele estar ofuscado con **R8** (o ProGuard). Si no preparas bien la configuración y el **mapping**, te quedas “en bragas”: crashes ilegibles y posible rotura por clases eliminadas o renombradas.

Esta guía resume lo que hay que tener listo **antes** de que Google revise la app y para cada nueva versión que subas.

---

## 1. Habilitar optimización en el build de release (Android)

En tu proyecto **Android** (o en el build Android que genera EAS/Expo), el build tipo **release** debe tener:

- **Minify (R8):** activado → ofusca y elimina código no usado.
- **Shrink resources:** activado → quita recursos no usados.
- **ProGuard/R8 rules:** fichero de reglas propio además del por defecto.

### Ejemplo en `build.gradle` (Kotlin DSL)

```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### Ejemplo en Groovy

```groovy
release {
    minifyEnabled true
    shrinkResources true
    proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
}
```

Usa **proguard-android-optimize.txt** (no el antiguo `proguard-android.txt` sin optimización).

---

## 2. Reglas ProGuard/R8 para no romper la app

R8 puede **eliminar** o **renombrar** clases que se usan por reflexión, serialización o desde el backend. Si no las proteges, la app puede fallar en release.

Crea o edita **`proguard-rules.pro`** (en el módulo `app`) y añade al menos:

### Modelos y DTOs (Gson, Moshi, Jackson, Retrofit)

Si usas JSON para API (p. ej. respuestas del backend VINO PRO):

```proguard
# Gson
-keepattributes Signature
-keepattributes *Annotation*
-dontwarn sun.misc.**
-keep class com.google.gson.** { *; }
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

# Modelos / DTOs que se serializan (ajusta el paquete al tuyo)
-keep class tu.paquete.app.model.** { *; }
-keep class tu.paquete.app.api.dto.** { *; }
```

Para **Moshi** (anotaciones `@JsonClass`):

```proguard
-keep class kotlin.Metadata { *; }
-keepclassmembers class * {
    @com.squareup.moshi.FromJson <methods>;
    @com.squareup.moshi.ToJson <methods>;
}
# Clases anotadas con generateAdapter = true
-keep class ** implements com.squareup.moshi.JsonAdapter
```

### Reflexión y anotaciones

Si usas reflexión o librerías que la usan (Hilt, Dagger, etc.):

```proguard
-keepattributes RuntimeVisibleAnnotations, RuntimeVisibleParameterAnnotations
-keepclassmembers class * {
    @* *;
}
```

### Actividades, Fragments, Application

```proguard
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Application
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider
```

### Opcional: no ofuscar solo para depurar

Solo si necesitas comprobar que el fallo es por ofuscación (luego quita):

```proguard
# -dontobfuscate
```

---

## 3. Subir el mapping a Play Console (para no quedarte en bragas con los crashes)

Sin el **mapping**, los crashes en producción salen con clases y métodos ofuscados (tipo `a.b.c.d()`). Google y tú necesitáis el fichero **mapping** de esa build para traducirlos a tu código real.

### Dónde está el mapping (build nativo Android)

Tras un build release:

```
app/build/outputs/mapping/release/mapping.txt
```

### Dónde subirlo en Play Console

1. Entra en [Play Console](https://play.google.com/console) y selecciona la app **VINO PRO**.
2. **Versión de la app** → elige la versión (p. ej. la que está “En revisión” o la última publicada).
3. Busca **Archivos de desofuscación** / **Deobfuscation files** (puede estar en **Android vitals** o dentro de la release).
4. Sube el **mapping.txt** correspondiente a **esa** versión exacta.

**Importante:** cada nueva versión (nuevo build release) genera un **mapping distinto**. Debes subir el mapping de esa versión; si no, los stack traces no cuadran.

### Si usas EAS Build (Expo)

En builds Android con EAS, el artefacto de la build suele incluir o generar un mapping. Revisa la salida de `eas build --platform android --profile production` y la [doc de EAS](https://docs.expo.dev/build-reference/android-builds/) para la ruta del mapping; luego súbelo manualmente en Play Console como arriba.

---

## 4. Comprobar que no hay errores de ofuscación

Antes de subir a Play:

1. Genera un **APK/AAB de release** (no debug).
2. Instálalo en un dispositivo o emulador y haz un **recorrido completo**: inicio, escáner, bodega, comunidad, mapa, login, etc.
3. Revisa que no haya crashes al abrir pantallas o al recibir datos del backend (ahí suelen fallar DTOs por ofuscación).
4. Si algo falla solo en release, añade **keep** para las clases o paquetes implicados en ese flujo.

---

## 5. Resumen checklist (para no quedarte en bragas)

| Paso | Qué hacer |
|------|-----------|
| 1 | `isMinifyEnabled true` y `isShrinkResources true` en **release**. |
| 2 | `proguardFiles`: `proguard-android-optimize.txt` + tu `proguard-rules.pro`. |
| 3 | En `proguard-rules.pro`: keep de **modelos/DTOs**, **reflexión** y **Activity/Application** según tu paquete. |
| 4 | Build release y **probar** la app de punta a punta. |
| 5 | Por **cada** versión que subas a Play: subir el **mapping.txt** de esa build en **Archivos de desofuscación**. |

Con esto, cuando Google revise la app y la ofusque, tú ya tendrás la ofuscación controlada y los crashes legibles en Play Console.

---

## Referencias

- [Habilitar optimización con R8 (Android)](https://developer.android.com/topic/performance/app-optimization/enable-app-optimization)
- [Desofuscar crashes en Play Console](https://support.google.com/googleplay/android-developer/answer/9848633)
- [Añadir reglas keep (ProGuard/R8)](https://developer.android.com/topic/performance/app-optimization/add-keep-rules)
- [Solucionar problemas de optimización R8](https://developer.android.com/topic/performance/app-optimization/troubleshoot-the-optimization)

---

*Guía creada a partir de buenas prácticas para R8/ProGuard y requisitos de Google Play. El proyecto Android puede estar en otro repositorio; esta doc sirve de referencia para el día de la revisión y cada release.*
