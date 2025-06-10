# player.py
from cards import Card

class Player:
    """
    플레이어 클래스 -
    이름, 포인트(초기 3000), 그리고 기본 카드 리스트(가위, 바위, 보)를 관리합니다.
    """
    def __init__(self, name: str):
        self.name = name
        self.points = 1000
        self.cards = [Card("가위"), Card("바위"), Card("보")]

    def bid_points(self, amount: int):
        """
        경매 입찰 시 사용 (하지만 auction.py에서는 직접 포인트 차감 처리)
        필요 시 참고용 함수.
        """
        if amount <= self.points:
            self.points -= amount
            return True
        return False

    def add_card(self, card):
        """새로운 카드 획득"""
        if isinstance(card, Card):
            self.cards.append(card)

    def use_card(self, card_name: str):
        """사용할 카드를 선택하여 제거 (가위, 바위, 보)"""
        for card in self.cards:
            if card.name == card_name:
                self.cards.remove(card)
                return True
        return False

def create_player():
    """플레이어 이름을 입력받아 Player 객체 생성"""
    name = input("📝 플레이어 이름을 입력하세요: ")
    return Player(name)
