import logging
from typing import List, Dict, Any, Optional
from .api_client import TarotAPI

logger = logging.getLogger(__name__)

def _validate_cards_count(cards: Optional[list], required: int) -> bool:
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
        text += f"**{position}:** {card.get('name', 'Неизвестная карта')}\n"
        if is_reversed:
            text += f"🔄 {card.get('rdesc', 'Описание отсутствует')}\n\n"
        else:
            text += f"⬆️ {card.get('desc', 'Описание отсутствует')}\n\n"
    
    return text

async def validate_cards(api: TarotAPI, required: int) -> Optional[list]:
    cards = await api.get_cards()
    return cards if _validate_cards_count(cards, required) else None