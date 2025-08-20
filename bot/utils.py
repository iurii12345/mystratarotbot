import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def validate_cards_count(cards: Optional[list], required: int) -> bool:
    if not cards:
        return False
    if len(cards) < required:
        logger.warning(f"Недостаточно карт: требуется {required}, доступно {len(cards)}")
        return False
    return True

def format_card_message(
    cards: List[Dict[str, Any]],
    positions: List[str],
    is_reversed_list: List[bool],
    title: str
) -> str:
    text = f"**{title}**\n\n"
    
    for card, position, is_reversed in zip(cards, positions, is_reversed_list):    
        if is_reversed:
            text += f"**{position}:** \n🔄 {card.get('name', 'Неизвестная карта')}\n"
            text += f"{card.get('rdesc', 'Описание отсутствует')}\n\n"
        else:
            text += f"**{position}:** \n⬆️ {card.get('name', 'Неизвестная карта')}\n"
            text += f"{card.get('desc', 'Описание отсутствует')}\n\n"
    
    return text