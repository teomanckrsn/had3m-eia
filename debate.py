"""Tartışma Modülü - Özel kişilikler oluştur ve tartıştır."""

import os
import json
from datetime import datetime

import ollama

from model_config import get_chat_model

MODEL_NAME = get_chat_model()
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PERSONAS_FILE = os.path.join(DATA_DIR, "personas.json")

# Karakter özellikleri — kullanıcı bunları seçip kişiliğe ekleyebilir
PERSONALITY_TRAITS = {
    # Motivasyon & Enerji
    "Hırslı": "Son derece hırslı ve hedef odaklısın. Büyük düşünür, sınırları zorlar, asla 'olmaz' demezsin.",
    "Pozitif": "Her zaman pozitif ve iyimsersin. Fırsatları görür, insanları motive eder, enerjin bulaşıcıdır.",
    "Sakin": "Sakin ve soğukkanlısın. Kriz anlarında bile panik yapmazsın, mantıklı ve dengeli kararlar verirsin.",
    "Agresif": "İş dünyasında agresif ve rekabetçisin. Hızlı hareket eder, fırsatları kapmak için yarışırsın.",

    # Düşünme Tarzı
    "Analitik": "Her şeyi veriye dayalı analiz edersin. Sayılar, grafikler ve istatistiklerle konuşursun.",
    "Yaratıcı": "Kutunun dışında düşünürsün. Alışılmadık fikirler üretir, yenilikçi çözümler sunarsın.",
    "Stratejik": "Uzun vadeli düşünür, satranç oynar gibi 3-5 hamle ileriye bakarsın.",
    "Pratik": "Teoriyle değil pratikte uygulama ile ilgilenirsin. 'Tamam ama bunu nasıl yapacağız?' dersin.",
    "Detaycı": "Hiçbir detayı kaçırmazsın. İnce eleyip sık dokursun, mükemmeliyetçisin.",

    # İletişim Tarzı
    "Diplomatik": "Nazik, ölçülü ve diplomatiksin. Kimseyi kırmadan eleştiri yaparsın.",
    "Dobra": "Lafı dolandırmazsın, ne düşünüyorsan söylersin. Dürüst ve açık sözlüsün.",
    "İkna Edici": "İnsanları ikna etmekte çok iyisin. Argümanlarını güçlü kurarsın.",
    "Dinleyici": "Önce dinler, sonra konuşursun. Karşı tarafı anlamaya çalışırsın.",

    # Risk & Karar
    "Risk Alan": "Hesaplanmış riskler almaktan çekinmezsin. 'Denemeden bilemeyiz' felsefesiyle hareket edersin.",
    "Temkinli": "Dikkatli ve temkinlisin. Her kararı iki kere düşünür, riskleri minimize edersin.",
    "Kararlı": "Hızlı karar verir ve arkasında durursun. Kararsızlıktan nefret edersin.",

    # İş Yaklaşımı
    "Müşteri Odaklı": "Her kararı müşterinin gözünden değerlendirirsin. Müşteri memnuniyeti her şeyin önünde.",
    "Maliyet Odaklı": "Bütçeye ve maliyete çok dikkat edersin. Gereksiz harcamalardan kaçınırsın.",
    "Büyüme Odaklı": "Büyüme ve ölçeklenme senin için en önemli şey. Pazar payı kazanmak istersin.",
    "Kalite Odaklı": "Kaliteden asla taviz vermezsin. 'Az ama öz' felsefesiyle çalışırsın.",
    "Hız Odaklı": "Hız senin için çok önemli. 'Mükemmel olmasın ama hızlı olsun, sonra düzeltiriz' dersin.",
}


def get_trait_categories() -> dict[str, list[str]]:
    """Özellikleri kategorilere ayırıp döndür."""
    categories = {
        "Motivasyon & Enerji": ["Hırslı", "Pozitif", "Sakin", "Agresif"],
        "Düşünme Tarzı": ["Analitik", "Yaratıcı", "Stratejik", "Pratik", "Detaycı"],
        "İletişim Tarzı": ["Diplomatik", "Dobra", "İkna Edici", "Dinleyici"],
        "Risk & Karar": ["Risk Alan", "Temkinli", "Kararlı"],
        "İş Yaklaşımı": ["Müşteri Odaklı", "Maliyet Odaklı", "Büyüme Odaklı", "Kalite Odaklı", "Hız Odaklı"],
    }
    return categories


def get_all_traits() -> list[str]:
    return list(PERSONALITY_TRAITS.keys())


def traits_to_description(traits: list[str]) -> str:
    """Seçilen özellikleri açıklama metnine çevir."""
    parts = []
    for t in traits:
        if t in PERSONALITY_TRAITS:
            parts.append(PERSONALITY_TRAITS[t])
    return " ".join(parts)

# Varsayılan kişilikler (ilk açılışta oluşturulur)
DEFAULT_PERSONAS = {
    "Kişisel Asistan": {
        "name": "Kişisel Asistan",
        "role": "Kişisel asistan",
        "description": (
            "Sen kullanıcının kişisel asistanısın. Önceliğin kullanıcının "
            "ihtiyaçlarını anlamak ve pratik çözümler sunmak. Organize, yardımsever "
            "ve çözüm odaklısın."
        ),
        "color": "#1a73e8",
    },
    "Şirket Yöneticisi": {
        "name": "Şirket Yöneticisi",
        "role": "CEO / Genel Müdür",
        "description": (
            "Sen bir şirketin genel müdürüsün. Stratejik düşünür, büyük resmi görür, "
            "risk-fayda analizleri yaparsın. Kararlarını şirketin uzun vadeli başarısına "
            "göre şekillendirirsin. Finansal sürdürülebilirlik ve büyüme senin için önemli."
        ),
        "color": "#2c3e50",
    },
    "Reklam Danışmanı": {
        "name": "Reklam Danışmanı",
        "role": "Pazarlama ve reklam uzmanı",
        "description": (
            "Sen deneyimli bir reklam ve pazarlama danışmanısın. Marka bilinirliği, "
            "hedef kitle analizi, kampanya stratejileri ve dijital pazarlama konularında "
            "uzmansın. Yaratıcı ve trend takipçisisin."
        ),
        "color": "#e74c3c",
    },
    "Finans Müdürü": {
        "name": "Finans Müdürü",
        "role": "CFO / Finans direktörü",
        "description": (
            "Sen şirketin finans müdürüsün. Bütçe, maliyet, kârlılık ve yatırım "
            "getirisi perspektifinden değerlendirme yaparsın. Sayılarla konuşur, "
            "riskleri finansal açıdan analiz edersin."
        ),
        "color": "#27ae60",
    },
    "Müşteri Temsilcisi": {
        "name": "Müşteri Temsilcisi",
        "role": "Müşteri deneyimi uzmanı",
        "description": (
            "Sen müşteri tarafını temsil ediyorsun. Müşteri memnuniyeti, kullanıcı "
            "deneyimi ve müşteri geri bildirimleri konusunda uzmansın. Her kararı "
            "müşterinin gözünden değerlendirirsin."
        ),
        "color": "#f39c12",
    },
}


class PersonaManager:
    """Kişilikleri yönetir - oluştur, düzenle, sil."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.personas = self._load()

    def _load(self) -> dict:
        if os.path.exists(PERSONAS_FILE):
            with open(PERSONAS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        # İlk açılış: varsayılanları kaydet
        self._save_dict(DEFAULT_PERSONAS)
        return dict(DEFAULT_PERSONAS)

    def _save_dict(self, data: dict):
        with open(PERSONAS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save(self):
        self._save_dict(self.personas)

    def get_names(self) -> list[str]:
        return list(self.personas.keys())

    def get(self, name: str) -> dict:
        return self.personas.get(name, {})

    def add(self, name: str, role: str, description: str, color: str = "#2b2b2b",
            traits: list[str] = None, relationships: dict = None):
        self.personas[name] = {
            "name": name,
            "role": role,
            "description": description,
            "color": color,
            "traits": traits or [],
            "relationships": relationships or {},
        }
        self._save()

    def set_relationship(self, from_name: str, to_name: str, opinion: str):
        """Kişilikler arası ilişki tanımla. ör: CEO → Finans Müdürü: 'Temkinli buluyorum'"""
        if from_name in self.personas:
            rels = self.personas[from_name].get("relationships", {})
            rels[to_name] = opinion
            self.personas[from_name]["relationships"] = rels
            self._save()

    def get_relationship(self, from_name: str, to_name: str) -> str:
        p = self.personas.get(from_name, {})
        return p.get("relationships", {}).get(to_name, "")

    def get_all_relationships(self, name: str) -> dict:
        """Bir kişiliğin tüm ilişkilerini döndür."""
        p = self.personas.get(name, {})
        return p.get("relationships", {})

    def remove(self, name: str):
        if name in self.personas:
            del self.personas[name]
            # Diğer kişiliklerdeki ilişkileri de temizle
            for p in self.personas.values():
                rels = p.get("relationships", {})
                if name in rels:
                    del rels[name]
            self._save()

    def get_system_prompt(self, name: str, talking_to: str = None) -> str:
        p = self.personas.get(name, {})
        prompt = f"Sen {p.get('role', 'bir uzman')}sın. {p.get('description', '')} "

        # Karakter özellikleri
        traits = p.get("traits", [])
        if traits:
            trait_desc = traits_to_description(traits)
            prompt += f"\n\nKarakter özelliklerin: {trait_desc} "

        # İlişkiler
        if talking_to:
            rel = p.get("relationships", {}).get(talking_to, "")
            if rel:
                prompt += f"\n\n{talking_to} hakkındaki düşüncen: {rel}. Bu düşüncen cevaplarına yansısın."

        prompt += "\nHer zaman Türkçe konuş. Kısa ve öz cevaplar ver."
        return prompt


# Global instance
persona_manager = PersonaManager()


def get_personality_names() -> list[str]:
    return persona_manager.get_names()


def get_persona_color(name: str) -> str:
    p = persona_manager.get(name)
    return p.get("color", "#2b2b2b")


def debate(topic: str, persona1: str, persona2: str, rounds: int = 2,
           on_message=None):
    """İki kişilik arasında tartışma yürüt (ilişkiler dahil)."""
    sys1 = persona_manager.get_system_prompt(persona1, talking_to=persona2)
    sys2 = persona_manager.get_system_prompt(persona2, talking_to=persona1)

    history1 = [{"role": "system", "content": sys1}]
    history2 = [{"role": "system", "content": sys2}]

    # İlk kişilik konuyu açar
    opening = (
        f"Şu konu hakkında profesyonel görüşünü paylaş "
        f"(kısa ve öz, max 3-4 cümle): {topic}"
    )
    history1.append({"role": "user", "content": opening})

    response1 = ollama.chat(model=MODEL_NAME, messages=history1)
    msg1 = response1["message"]["content"]
    history1.append({"role": "assistant", "content": msg1})

    if on_message:
        on_message(persona1, msg1)

    for i in range(rounds):
        # Kişilik 2 cevap verir
        prompt2 = (
            f"{persona1} ({persona_manager.get(persona1).get('role', '')}) "
            f"şöyle diyor: \"{msg1}\"\n\n"
            f"Kendi uzmanlık alanından bu görüşe cevap ver (kısa ve öz, max 3-4 cümle):"
        )
        history2.append({"role": "user", "content": prompt2})
        response2 = ollama.chat(model=MODEL_NAME, messages=history2)
        msg2 = response2["message"]["content"]
        history2.append({"role": "assistant", "content": msg2})

        if on_message:
            on_message(persona2, msg2)

        if i < rounds - 1:
            # Kişilik 1 yanıt verir
            prompt1 = (
                f"{persona2} ({persona_manager.get(persona2).get('role', '')}) "
                f"şöyle diyor: \"{msg2}\"\n\n"
                f"Kendi uzmanlık alanından bu görüşe cevap ver (kısa ve öz, max 3-4 cümle):"
            )
            history1.append({"role": "user", "content": prompt1})
            response1 = ollama.chat(model=MODEL_NAME, messages=history1)
            msg1 = response1["message"]["content"]
            history1.append({"role": "assistant", "content": msg1})

            if on_message:
                on_message(persona1, msg1)

    # Moderatör özeti
    summary_prompt = (
        f"Konu: {topic}\n\n"
        f"{persona1} ve {persona2} bu konuyu tartıştı.\n"
        f"Tartışmayı özetle, her iki tarafın güçlü argümanlarını belirt, "
        f"ve somut bir strateji/aksiyon önerisi sun. Kısa tut."
    )
    summary_resp = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen tarafsız bir iş stratejisti ve moderatörsün. Her zaman Türkçe konuş."},
            {"role": "user", "content": summary_prompt},
        ],
    )
    summary = summary_resp["message"]["content"]

    if on_message:
        on_message("🏛 Moderatör", summary)

    return summary
