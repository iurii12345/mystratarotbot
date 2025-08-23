def interpret_single_card(card, is_reversed):
    card_name = card.get("name", "Неизвестная карта")
    interpretation = f"📖 **Толкование карты {card_name}**\n\n"
    if is_reversed:
        interpretation += f"🔄 **Перевернутое положение:**\n{card.get('rdesc', 'Описание отсутствует')}\n\n"
        interpretation += f"💡 **Совет:** {card.get('radvice', 'Примите ситуацию как есть')}"
    else:
        interpretation += f"⬆️ **Прямое положение:**\n{card.get('desc', 'Описание отсутствует')}\n\n"
        interpretation += f"💡 **Совет:** {card.get('advice', 'Доверьтесь своей интуиции')}"
    return interpretation

def interpret_daily_spread(cards, positions, is_reversed_list):
    interpretation = "🌅 **Толкование расклада на день**\n\n"
    parts = []
    for card, pos, rev in zip(cards, positions, is_reversed_list):
        card_name = card.get("name", "Неизвестная карта")
        if rev:
            desc = card.get("rdesc", "Описание отсутствует")
            advice = card.get("radvice", "Примите ситуацию как есть")
            parts.append(
                f"**{pos}** — {card_name}\n🔄 Перевернутое положение:\n{desc}\n💡 Совет: {advice}\n"
            )
        else:
            desc = card.get("desc", "Описание отсутствует")
            advice = card.get("advice", "Доверьтесь своей интуиции")
            parts.append(
                f"**{pos}** — {card_name}\n⬆️ Прямое положение:\n{desc}\n💡 Совет: {advice}\n"
            )
    interpretation += "\n".join(parts)
    return interpretation

def interpret_love_spread(cards, positions, is_reversed_list):
    interpretation = "💕 **Толкование расклада на любовь**\n\n"
    parts = []
    for card, pos, rev in zip(cards, positions, is_reversed_list):
        card_name = card.get("name", "Неизвестная карта")
        if rev:
            desc = card.get("rdesc", "Описание отсутствует")
            advice = card.get("radvice", "Примите ситуацию как есть")
            parts.append(
                f"**{pos}** — {card_name}\n🔄 Перевернутое положение:\n{desc}\n💡 Совет: {advice}\n"
            )
        else:
            desc = card.get("desc", "Описание отсутствует")
            advice = card.get("advice", "Доверьтесь своей интуиции")
            parts.append(
                f"**{pos}** — {card_name}\n⬆️ Прямое положение:\n{desc}\n💡 Совет: {advice}\n"
            )
    interpretation += "\n".join(parts)
    return interpretation

def interpret_work_spread(cards, positions, is_reversed_list):
    interpretation = "💼 **Толкование расклада на работу**\n\n"
    parts = []
    for card, pos, rev in zip(cards, positions, is_reversed_list):
        card_name = card.get("name", "Неизвестная карта")
        if rev:
            desc = card.get("rdesc", "Описание отсутствует")
            advice = card.get("radvice", "Примите ситуацию как есть")
            parts.append(
                f"**{pos}** — {card_name}\n🔄 Перевернутое положение:\n{desc}\n💡 Совет: {advice}\n"
            )
        else:
            desc = card.get("desc", "Описание отсутствует")
            advice = card.get("advice", "Доверьтесь своей интуиции")
            parts.append(
                f"**{pos}** — {card_name}\n⬆️ Прямое положение:\n{desc}\n💡 Совет: {advice}\n"
            )
    interpretation += "\n".join(parts)
    return interpretation

def interpret_celtic_cross(cards, positions, is_reversed_list):
    interpretation = "🏰 **Толкование расклада «Кельтский крест»**\n\n"
    parts = []
    for card, pos, rev in zip(cards, positions, is_reversed_list):
        card_name = card.get("name", "Неизвестная карта")
        if rev:
            desc = card.get("rdesc", "Описание отсутствует")
            advice = card.get("radvice", "Примите ситуацию как есть")
            parts.append(
                f"**{pos}** — {card_name}\n🔄 Перевернутое положение:\n{desc}\n💡 Совет: {advice}\n"
            )
        else:
            desc = card.get("desc", "Описание отсутствует")
            advice = card.get("advice", "Доверьтесь своей интуиции")
            parts.append(
                f"**{pos}** — {card_name}\n⬆️ Прямое положение:\n{desc}\n💡 Совет: {advice}\n"
            )
    interpretation += "\n".join(parts)
    return interpretation
