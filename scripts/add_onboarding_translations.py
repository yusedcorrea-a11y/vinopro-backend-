# -*- coding: utf-8 -*-
"""Add onboarding block to zh, ja, ko, hi, ar (minified JSON)."""
import json
import re

TRANSLATIONS = {
    "ja": {
        "titulo_ubicacion": "位置情報の許可",
        "descripcion_ubicacion": "近くの場所、地図、Guía Repsol を表示するには位置情報が必要です。今すぐまたは後で許可できます。",
        "permitir": "許可",
        "ahora_no": "後で",
        "titulo_idioma": "言語を選択",
        "elige_idioma": "アプリとソムリエAIはこの言語を使用します。メニューで後から変更できます。",
        "continuar": "続ける",
        "titulo_registro": "アカウント作成",
        "descripcion_registro": "セラーを保存し、他のビネロとチャットし、すべての機能を使うには、今すぐ登録してください。",
        "btn_registrarme": "登録",
    },
    "ko": {
        "titulo_ubicacion": "위치 권한",
        "descripcion_ubicacion": "주변 장소, 지도, Guía Repsol을 보여드리려면 위치가 필요합니다. 지금 또는 나중에 허용할 수 있습니다.",
        "permitir": "허용",
        "ahora_no": "나중에",
        "titulo_idioma": "언어 선택",
        "elige_idioma": "앱과 소믈리에 AI가 이 언어를 사용합니다. 메뉴에서 나중에 변경할 수 있습니다.",
        "continuar": "계속",
        "titulo_registro": "계정 만들기",
        "descripcion_registro": "와인창고 저장, 다른 비네로와 채팅, 모든 기능 사용을 위해 지금 가입하세요.",
        "btn_registrarme": "가입",
    },
    "hi": {
        "titulo_ubicacion": "लोकेशन अनुमति",
        "descripcion_ubicacion": "आस-पास की जगहें, मानचित्र और Guía Repsol दिखाने के लिए हमें आपका लोकेशन चाहिए। अभी या बाद में अनुमति दे सकते हैं।",
        "permitir": "अनुमति दें",
        "ahora_no": "अभी नहीं",
        "titulo_idioma": "अपनी भाषा चुनें",
        "elige_idioma": "ऐप और सोमेलियर AI इस भाषा का उपयोग करेंगे। मेनू में बाद में बदल सकते हैं।",
        "continuar": "जारी रखें",
        "titulo_registro": "खाता बनाएं",
        "descripcion_registro": "सेलर सहेजने, अन्य वाइनरो से चैट करने और सभी सुविधाओं के लिए अभी रजिस्टर करें।",
        "btn_registrarme": "रजिस्टर",
    },
    "ar": {
        "titulo_ubicacion": "إذن الموقع",
        "descripcion_ubicacion": "لعرض الأماكن القريبة والخرائط ودليل ريبسول في منطقتك نحتاج موقعك. يمكنك السماح الآن أو لاحقاً.",
        "permitir": "السماح",
        "ahora_no": "لاحقاً",
        "titulo_idioma": "اختر لغتك",
        "elige_idioma": "التطبيق والسوميلييه بالذكاء الاصطناعي سيستخدمان هذه اللغة. يمكنك تغييرها لاحقاً من القائمة.",
        "continuar": "متابعة",
        "titulo_registro": "إنشاء حسابك",
        "descripcion_registro": "لحفظ قبوك والتواصل مع فينيروس آخرين واستخدام كل المزايا، سجّل في دقيقة.",
        "btn_registrarme": "التسجيل",
    },
}

def main():
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    trans_dir = os.path.join(root, "data", "translations")
    for lang, ob in TRANSLATIONS.items():
        path = os.path.join(trans_dir, lang + ".json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "onboarding" in data:
            print(lang, "already has onboarding")
            continue
        data["onboarding"] = ob
        # Insert before "error" key to keep order similar
        new_data = {}
        for k, v in data.items():
            if k == "error":
                new_data["onboarding"] = ob
            new_data[k] = v
        with open(path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False)
        print(lang, "ok")

if __name__ == "__main__":
    main()
