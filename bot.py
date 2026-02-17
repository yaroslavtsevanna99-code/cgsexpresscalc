import os
import math
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==========================================================
# 1) КАЛЬКУЛЯТОР (твоя логика)
# ==========================================================

@dataclass(frozen=True)
class Bracket:
    min_density: float
    max_density: float
    price_per_kg: Optional[float] = None


# Тарифы карго (русские названия)
# режимы: "Экспресс", "Стандарт", "Медленно"
RATES: Dict[Tuple[str, str], Dict[str, Any]] = {
    ("Инструменты", "Экспресс"): {
        "срок": "12-15",
        "price_under_100_m3": 250.0,
        "brackets": [
            Bracket(400, math.inf, 1.1),
            Bracket(350, 400, 1.2),
            Bracket(300, 350, 1.3),
            Bracket(250, 300, 1.4),
            Bracket(200, 250, 1.5),
            Bracket(190, 200, 1.6),
            Bracket(180, 190, 1.7),
            Bracket(170, 180, 1.8),
            Bracket(160, 170, 1.9),
            Bracket(150, 160, 2.0),
            Bracket(140, 150, 2.1),
            Bracket(130, 140, 2.2),
            Bracket(120, 130, 2.3),
            Bracket(110, 120, 2.4),
            Bracket(100, 110, 2.5),
        ],
    },
    ("Инструменты", "Стандарт"): {
        "срок": "15-20",
        "price_under_100_m3": 240.0,
        "brackets": [
            Bracket(400, math.inf, 1.0),
            Bracket(350, 400, 1.1),
            Bracket(300, 350, 1.2),
            Bracket(250, 300, 1.3),
            Bracket(200, 250, 1.4),
            Bracket(190, 200, 1.5),
            Bracket(180, 190, 1.6),
            Bracket(170, 180, 1.7),
            Bracket(160, 170, 1.8),
            Bracket(150, 160, 1.9),
            Bracket(140, 150, 2.0),
            Bracket(130, 140, 2.1),
            Bracket(120, 130, 2.2),
            Bracket(110, 120, 2.3),
            Bracket(100, 110, 2.4),
        ],
    },

    ("Автозапчасти", "Стандарт"): {
        "срок": "15-20",
        "price_under_100_m3": 260.0,
        "brackets": [
            Bracket(800, math.inf, 1.0),
            Bracket(600, 800, 1.1),
            Bracket(400, 600, 1.2),
            Bracket(350, 400, 1.3),
            Bracket(300, 350, 1.4),
            Bracket(250, 300, 1.5),
            Bracket(200, 250, 1.6),
            Bracket(190, 200, 1.7),
            Bracket(180, 190, 1.8),
            Bracket(170, 180, 1.9),
            Bracket(160, 170, 2.0),
            Bracket(150, 160, 2.1),
            Bracket(140, 150, 2.2),
            Bracket(130, 140, 2.3),
            Bracket(120, 130, 2.4),
            Bracket(110, 120, 2.5),
            Bracket(100, 110, 2.6),
        ],
    },
    ("Автозапчасти", "Экспресс"): {
        "срок": "12-15",
        "price_under_100_m3": 270.0,
        "brackets": [
            Bracket(800, math.inf, 1.1),
            Bracket(600, 800, 1.2),
            Bracket(400, 600, 1.3),
            Bracket(350, 400, 1.4),
            Bracket(300, 350, 1.5),
            Bracket(250, 300, 1.6),
            Bracket(200, 250, 1.7),
            Bracket(190, 200, 1.8),
            Bracket(180, 190, 1.9),
            Bracket(170, 180, 2.0),
            Bracket(160, 170, 2.1),
            Bracket(150, 160, 2.2),
            Bracket(140, 150, 2.3),
            Bracket(130, 140, 2.4),
            Bracket(120, 130, 2.5),
            Bracket(110, 120, 2.6),
            Bracket(100, 110, 2.7),
        ],
    },

    ("Игрушки", "Стандарт"): {
        "срок": "15-20",
        "price_under_100_m3": 250.0,
        "brackets": [
            Bracket(250, math.inf, 1.4),
            Bracket(200, 250, 1.5),
            Bracket(190, 200, 1.6),
            Bracket(180, 190, 1.7),
            Bracket(170, 180, 1.8),
            Bracket(160, 170, 1.9),
            Bracket(150, 160, 2.0),
            Bracket(140, 150, 2.1),
            Bracket(130, 140, 2.2),
            Bracket(120, 130, 2.3),
            Bracket(110, 120, 2.4),
            Bracket(100, 110, 2.5),
        ],
    },
    ("Игрушки", "Экспресс"): {
        "срок": "12-15",
        "price_under_100_m3": 260.0,
        "brackets": [
            Bracket(250, math.inf, 1.5),
            Bracket(200, 250, 1.6),
            Bracket(190, 200, 1.7),
            Bracket(180, 190, 1.8),
            Bracket(170, 180, 1.9),
            Bracket(160, 170, 2.0),
            Bracket(150, 160, 2.1),
            Bracket(140, 150, 2.2),
            Bracket(130, 140, 2.3),
            Bracket(120, 130, 2.4),
            Bracket(110, 120, 2.5),
            Bracket(100, 110, 2.6),
        ],
    },

    ("Бытовая техника", "Стандарт"): {
        "срок": "15-20",
        "price_under_100_m3": 290.0,
        "brackets": [
            Bracket(400, math.inf, 1.5),
            Bracket(350, 400, 1.6),
            Bracket(300, 350, 1.7),
            Bracket(250, 300, 1.8),
            Bracket(200, 250, 1.9),
            Bracket(190, 200, 2.0),
            Bracket(180, 190, 2.1),
            Bracket(170, 180, 2.2),
            Bracket(160, 170, 2.3),
            Bracket(150, 160, 2.4),
            Bracket(140, 150, 2.5),
            Bracket(130, 140, 2.6),
            Bracket(120, 130, 2.7),
            Bracket(110, 120, 2.8),
            Bracket(100, 110, 2.9),
        ],
    },
    ("Бытовая техника", "Экспресс"): {
        "срок": "12-15",
        "price_under_100_m3": 300.0,
        "brackets": [
            Bracket(400, math.inf, 1.6),
            Bracket(350, 400, 1.7),
            Bracket(300, 350, 1.8),
            Bracket(250, 300, 1.9),
            Bracket(200, 250, 2.0),
            Bracket(190, 200, 2.1),
            Bracket(180, 190, 2.2),
            Bracket(170, 180, 2.3),
            Bracket(160, 170, 2.4),
            Bracket(150, 160, 2.5),
            Bracket(140, 150, 2.6),
            Bracket(130, 140, 2.7),
            Bracket(120, 130, 2.8),
            Bracket(110, 120, 2.9),
            Bracket(100, 110, 3.0),
        ],
    },

    ("TIR (общие товары)", "Экспресс"): {
        "срок": "12-15",
        "price_under_100_m3": 280.0,
        "brackets": [
            Bracket(800, math.inf, 1.2),
            Bracket(600, 800, 1.3),
            Bracket(400, 600, 1.4),
            Bracket(350, 400, 1.5),
            Bracket(300, 350, 1.6),
            Bracket(250, 300, 1.7),
            Bracket(200, 250, 1.8),
            Bracket(190, 200, 1.9),
            Bracket(180, 190, 2.0),
            Bracket(170, 180, 2.1),
            Bracket(160, 170, 2.2),
            Bracket(150, 160, 2.3),
            Bracket(140, 150, 2.4),
            Bracket(130, 140, 2.5),
            Bracket(120, 130, 2.6),
            Bracket(110, 120, 2.7),
            Bracket(100, 110, 2.8),
        ],
    },

    ("Одежда", "Медленно"): {
        "срок": "25-30",
        "price_under_100_m3": None,
        "brackets": [
            Bracket(300, 350, 1.9),
            Bracket(250, 300, 2.0),
            Bracket(200, 250, 2.1),
        ],
    },
    ("Одежда", "Стандарт"): {
        "срок": "18-25",
        "price_under_100_m3": None,
        "brackets": [
            Bracket(300, 350, 2.1),
            Bracket(250, 300, 2.2),
            Bracket(200, 250, 2.3),
        ],
    },
    ("Одежда", "Экспресс"): {
        "срок": "13-15",
        "price_under_100_m3": None,
        "brackets": [
            Bracket(300, 350, 2.5),
            Bracket(250, 300, 2.6),
            Bracket(200, 250, 2.7),
        ],
    },
}

# Белая доставка
WHITE_CUSTOMS_ON_US_PER_M3 = 180.0
WHITE_CUSTOMS_ON_CLIENT_PER_KG = 140.0
WHITE_FIXED_FEE = 500.0
WHITE_EXTRA_PACK_PER_M3 = 20.0
WHITE_INSURANCE_RATE = 0.01


def pick_cargo_service(тип_товара: str, желаемые_дни: int) -> str:
    available = [svc for (ct, svc) in RATES.keys() if ct == тип_товара]
    if not available:
        raise ValueError(f"Неизвестный тип товара: {тип_товара}")

    if желаемые_дни <= 15 and "Экспресс" in available:
        return "Экспресс"
    if желаемые_дни <= 20 and "Стандарт" in available:
        return "Стандарт"
    if желаемые_дни > 20 and "Медленно" in available:
        return "Медленно"

    for svc in ["Медленно", "Стандарт", "Экспресс"]:
        if svc in available:
            return svc
    return available[0]


def find_cargo_rate(тип_товара: str, режим: str, плотность: float) -> Dict[str, object]:
    table = RATES[(тип_товара, режим)]
    under_100_m3 = table.get("price_under_100_m3")

    if плотность < 100:
        if under_100_m3 is None:
            raise ValueError(f"Для {тип_товара}/{режим} нет тарифа <100 кг/м³ (по кубу).")
        return {"billing": "per_m3", "rate": float(under_100_m3), "срок": table["срок"]}

    for b in table["brackets"]:
        if b.min_density <= плотность < b.max_density:
            return {"billing": "per_kg", "rate": float(b.price_per_kg), "срок": table["срок"]}

    raise ValueError(f"Плотность {плотность:.2f} кг/м³ не попала ни в один диапазон.")


def calc_delivery(
    тип_доставки: str,
    тип_товара: str,
    желаемые_дни: int,
    вес_кг: float,
    объем_м3: float,
    стоимость_товара_usd: Optional[float] = None,
    оформление_нашей_компанией: Optional[bool] = None,
) -> Dict[str, object]:

    if вес_кг <= 0 or объем_м3 <= 0:
        raise ValueError("Вес и объём должны быть > 0")

    плотность = вес_кг / объем_м3

    if тип_доставки == "карго":
        режим = pick_cargo_service(тип_товара, желаемые_дни)
        info = find_cargo_rate(тип_товара, режим, плотность)

        if info["billing"] == "per_kg":
            total = info["rate"] * вес_кг
            eff = info["rate"]
            detail = f"{info['rate']:.2f} $/кг × {вес_кг:.2f} кг"
        else:
            total = info["rate"] * объем_м3
            eff = total / вес_кг
            detail = f"{info['rate']:.2f} $/м³ × {объем_м3:.3f} м³ (экв. {eff:.4f} $/кг)"

        return {
            "тип": "карго",
            "товар": тип_товара,
            "режим": режим,
            "прайс_срок": info["срок"],
            "плотность": round(плотность, 2),
            "итого_usd": round(total, 2),
            "эффективно_за_кг": round(eff, 4),
            "деталь": detail,
        }

    if тип_доставки == "белая":
        if оформление_нашей_компанией is None:
            raise ValueError("Для белой доставки нужно выбрать оформление: на нас/на клиенте")

        pack = WHITE_EXTRA_PACK_PER_M3 * объем_м3
        fixed = WHITE_FIXED_FEE

        if оформление_нашей_компанией:
            base = WHITE_CUSTOMS_ON_US_PER_M3 * объем_м3
            base_txt = f"{WHITE_CUSTOMS_ON_US_PER_M3:.2f} $/м³ × {объем_м3:.3f} м³"
            who = "наша компания"
        else:
            base = WHITE_CUSTOMS_ON_CLIENT_PER_KG * вес_кг
            base_txt = f"{WHITE_CUSTOMS_ON_CLIENT_PER_KG:.2f} $/кг × {вес_кг:.2f} кг"
            who = "клиент"

        if стоимость_товара_usd is None:
            subtotal = base + fixed + pack
            return {
                "тип": "белая",
                "оформление": who,
                "плотность": round(плотность, 2),
                "итого_usd": f"{subtotal:.2f} $ + 1% от стоимости товара",
                "деталь": f"{base_txt} + {fixed:.2f}$ + {WHITE_EXTRA_PACK_PER_M3:.2f}$/м³×{объем_м3:.3f}м³ + 1% от стоимости товара",
            }

        if стоимость_товара_usd < 0:
            raise ValueError("Стоимость товара не может быть отрицательной")

        ins = стоимость_товара_usd * WHITE_INSURANCE_RATE
        total = base + fixed + pack + ins
        return {
            "тип": "белая",
            "оформление": who,
            "плотность": round(плотность, 2),
            "итого_usd": round(total, 2),
            "деталь": f"{base_txt} + {fixed:.2f}$ + {WHITE_EXTRA_PACK_PER_M3:.2f}$/м³×{объем_м3:.3f}м³ + 1%×{стоимость_товара_usd:.2f}$={ins:.2f}$",
        }

    raise ValueError("тип_доставки должен быть 'карго' или 'белая'")


# ==========================================================
# 2) TELEGRAM BOT: кнопки + пошаговый ввод
# ==========================================================

CHOOSE_DELIVERY, CARGO_TYPE, CUSTOMS_TYPE, ASK_DAYS, ASK_WEIGHT, ASK_VOLUME, ASK_HAS_VALUE, ASK_VALUE, SHOW_RESULT = range(9)

def kb(rows):
    return InlineKeyboardMarkup(rows)

def start_keyboard():
    return kb([
        [InlineKeyboardButton("🚚 Карго", callback_data="delivery:cargo")],
        [InlineKeyboardButton("📄 Белая доставка", callback_data="delivery:white")],
    ])

def back_to_start_keyboard():
    return kb([[InlineKeyboardButton("🔁 Новый расчёт", callback_data="restart")]])

def cargo_type_keyboard():
    types_ = sorted({ct for (ct, _) in RATES.keys()})
    rows = []
    for t in types_:
        rows.append([InlineKeyboardButton(t, callback_data=f"cargo_type:{t}")])
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="restart")])
    return kb(rows)

def customs_keyboard():
    return kb([
        [InlineKeyboardButton("Оформление на нашей компании", callback_data="customs:us")],
        [InlineKeyboardButton("Оформление на клиенте", callback_data="customs:client")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="restart")],
    ])

def yes_no_value_keyboard():
    return kb([
        [InlineKeyboardButton("Да, есть стоимость товара", callback_data="has_value:yes")],
        [InlineKeyboardButton("Нет, стоимости нет", callback_data="has_value:no")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="restart")],
    ])

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет! Я калькулятор доставки.\n\n"
        "Выбери тип доставки кнопкой ниже 👇"
    )
    await update.message.reply_text(text, reply_markup=start_keyboard())
    return CHOOSE_DELIVERY

async def on_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("Ок, новый расчёт. Выбери тип доставки 👇", reply_markup=start_keyboard())
    return CHOOSE_DELIVERY

async def choose_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "delivery:cargo":
        context.user_data["delivery"] = "карго"
        await query.edit_message_text("Выбери тип товара (карго):", reply_markup=cargo_type_keyboard())
        return CARGO_TYPE

    if data == "delivery:white":
        context.user_data["delivery"] = "белая"
        await query.edit_message_text("Белая доставка: кто оформляет таможню?", reply_markup=customs_keyboard())
        return CUSTOMS_TYPE

    await query.edit_message_text("Не понял выбор. Нажми /start заново.")
    return ConversationHandler.END

async def choose_cargo_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("cargo_type:"):
        cargo_type = query.data.split(":", 1)[1]
        context.user_data["cargo_type"] = cargo_type
        await query.edit_message_text(
            "Ок. Теперь введи желаемый срок доставки (дней), например: 15\n\n(Можно просто числом)"
        )
        return ASK_DAYS

    if query.data == "restart":
        return await on_restart(update, context)

    await query.edit_message_text("Не понял тип товара. Нажми /start.")
    return ConversationHandler.END

async def choose_customs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "customs:us":
        context.user_data["customs_on_us"] = True
    elif query.data == "customs:client":
        context.user_data["customs_on_us"] = False
    elif query.data == "restart":
        return await on_restart(update, context)
    else:
        await query.edit_message_text("Не понял выбор. Нажми /start.")
        return ConversationHandler.END

    await query.edit_message_text("Введи желаемый срок доставки (дней), например: 15")
    return ASK_DAYS

async def ask_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip()
    try:
        days = int(txt)
        if days <= 0:
            raise ValueError
    except Exception:
        await update.message.reply_text("Нужно число дней (например 15). Попробуй ещё раз:")
        return ASK_DAYS

    context.user_data["days"] = days
    await update.message.reply_text("Введи вес (кг), например: 300")
    return ASK_WEIGHT

async def ask_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip().replace(",", ".")
    try:
        w = float(txt)
        if w <= 0:
            raise ValueError
    except Exception:
        await update.message.reply_text("Нужен вес в кг (например 300). Попробуй ещё раз:")
        return ASK_WEIGHT

    context.user_data["weight"] = w
    await update.message.reply_text("Введи объём (м³), например: 1.5")
    return ASK_VOLUME

async def ask_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip().replace(",", ".")
    try:
        v = float(txt)
        if v <= 0:
            raise ValueError
    except Exception:
        await update.message.reply_text("Нужен объём в м³ (например 1.5). Попробуй ещё раз:")
        return ASK_VOLUME

    context.user_data["volume"] = v

    # Для белой спросим про стоимость товара
    if context.user_data.get("delivery") == "белая":
        await update.message.reply_text("Есть стоимость товара (для страховки 1%)?", reply_markup=yes_no_value_keyboard())
        return ASK_HAS_VALUE

    # Для карго сразу считаем
    return await show_result_from_data(update, context)

async def ask_has_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "has_value:yes":
        context.user_data["has_value"] = True
        await query.edit_message_text("Ок. Введи стоимость товара (USD), например: 10000")
        return ASK_VALUE

    if query.data == "has_value:no":
        context.user_data["has_value"] = False
        context.user_data["goods_value"] = None
        # считаем сразу
        return await show_result_from_data(update, context, from_callback=True)

    if query.data == "restart":
        return await on_restart(update, context)

    await query.edit_message_text("Не понял. Нажми /start.")
    return ConversationHandler.END

async def ask_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip().replace(",", ".")
    try:
        val = float(txt)
        if val < 0:
            raise ValueError
    except Exception:
        await update.message.reply_text("Нужна стоимость товара в USD (например 10000). Попробуй ещё раз:")
        return ASK_VALUE

    context.user_data["goods_value"] = val
    return await show_result_from_data(update, context)

def format_result(res: Dict[str, object]) -> str:
    if res.get("тип") == "карго":
        return (
            "✅ Результат (Карго)\n"
            f"Товар: {res.get('товар')}\n"
            f"Режим: {res.get('режим')} (прайс срок {res.get('прайс_срок')} дней)\n"
            f"Плотность: {res.get('плотность')} кг/м³\n"
            f"Итого: {res.get('итого_usd')} $\n"
            f"Эффективно за кг: {res.get('эффективно_за_кг')} $/кг\n"
            f"Расчёт: {res.get('деталь')}"
        )
    else:
        return (
            "✅ Результат (Белая доставка)\n"
            f"Оформление: {res.get('оформление')}\n"
            f"Плотность: {res.get('плотность')} кг/м³\n"
            f"Итого: {res.get('итого_usd')}\n"
            f"Расчёт: {res.get('деталь')}"
        )

async def show_result_from_data(update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool=False):
    delivery = context.user_data.get("delivery")
    days = context.user_data.get("days")
    weight = context.user_data.get("weight")
    volume = context.user_data.get("volume")

    try:
        if delivery == "карго":
            cargo_type = context.user_data.get("cargo_type")
            res = calc_delivery("карго", cargo_type, int(days), float(weight), float(volume))
        else:
            customs_on_us = context.user_data.get("customs_on_us")
            goods_value = context.user_data.get("goods_value", None)
            res = calc_delivery(
                "белая",
                "(не требуется)",
                int(days),
                float(weight),
                float(volume),
                стоимость_товара_usd=(None if goods_value is None else float(goods_value)),
                оформление_нашей_компанией=bool(customs_on_us),
            )
    except Exception as e:
        msg = f"❌ Ошибка расчёта: {e}\n\nНажми «Новый расчёт» и попробуй ещё раз."
        if from_callback:
            await update.callback_query.edit_message_text(msg, reply_markup=back_to_start_keyboard())
        else:
            await update.message.reply_text(msg, reply_markup=back_to_start_keyboard())
        return ConversationHandler.END

    text = format_result(res)

    if from_callback:
        await update.callback_query.edit_message_text(text, reply_markup=back_to_start_keyboard())
    else:
        await update.message.reply_text(text, reply_markup=back_to_start_keyboard())

    return ConversationHandler.END


def build_app() -> Application:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не задан BOT_TOKEN. Пример: $env:BOT_TOKEN=\"...\"")

    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            CHOOSE_DELIVERY: [
                CallbackQueryHandler(on_restart, pattern="^restart$"),
                CallbackQueryHandler(choose_delivery, pattern="^delivery:(cargo|white)$"),
            ],
            CARGO_TYPE: [
                CallbackQueryHandler(on_restart, pattern="^restart$"),
                CallbackQueryHandler(choose_cargo_type, pattern="^cargo_type:"),
            ],
            CUSTOMS_TYPE: [
                CallbackQueryHandler(on_restart, pattern="^restart$"),
                CallbackQueryHandler(choose_customs, pattern="^customs:(us|client)$"),
            ],
            ASK_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_days)],
            ASK_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_weight)],
            ASK_VOLUME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_volume)],
            ASK_HAS_VALUE: [
                CallbackQueryHandler(on_restart, pattern="^restart$"),
                CallbackQueryHandler(ask_has_value, pattern="^has_value:(yes|no)$"),
            ],
            ASK_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_value)],
        },
        fallbacks=[CommandHandler("start", cmd_start)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    # На всякий: если нажали "Новый расчёт" после результата
    app.add_handler(CallbackQueryHandler(on_restart, pattern="^restart$"))

    return app


def main():
    app = build_app()
    app.run_polling()


if __name__ == "__main__":
    main()
