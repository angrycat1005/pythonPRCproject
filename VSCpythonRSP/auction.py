import random
from cards import Card

class Auction:
    """
    경매 시스템 클래스:
    - 경매에 참가할 카드(예: "특별 가위", "특별 바위", "특별 보")를 랜덤으로 선택합니다.
    - 플레이어는 직접 입찰 금액을 입력하고, 
      AI는 100 ~ 500 포인트 범위 내에서 랜덤하게 입찰합니다.
    - 입찰 금액은 낙찰한 쪽에만 차감됩니다.
    - 경매 전에 현재 경매에 올라간 카드가 무엇인지 출력됩니다.
    """
    def __init__(self):
        self.auction_cards = ["가위", "바위", "보"]

    def collect_bids(self, player, ai):
        # 경매에 올라갈 카드를 랜덤 선택 후 출력
        current_card = random.choice(self.auction_cards)
        print(f"\n-- 경매 카드 공개: {current_card} --")
        
        # 플레이어 입찰: 최소 100 포인트 이상, 현재 포인트 이하여야 함.
        try:
            bid_player = int(input(f"{player.name}, {current_card} 경매에 입찰할 금액을 입력하세요 (최소 100): "))
        except ValueError:
            bid_player = 0

        if bid_player < 100 or bid_player > player.points:
            print(f"{player.name}의 입찰 금액({bid_player})이 유효하지 않습니다. (최소 100, 현재 가진 포인트: {player.points})")
            bid_player = 0
        else:
            # 입찰 금액은 여기서 차감하지 않고, 낙찰 결과에 따라 차감합니다.
            print(f"{player.name}가 {bid_player} 포인트로 입찰했습니다.")

        # AI 입찰: 남은 포인트가 있으면 100 ~ 500 범위 내에서 입찰 (단, AI가 가진 포인트보다 클 경우 AI의 포인트만 사용)
        if ai.points >= 100:
            bid_ai = random.randint(100, 500)
            bid_ai = min(bid_ai, ai.points)
            print(f"{ai.name}가 {bid_ai} 포인트로 입찰했습니다.")
        else:
            bid_ai = 0
            print(f"{ai.name}은(는) 입찰할 포인트가 부족합니다.")

        # 입찰 결과 결정
        if bid_player == bid_ai:
            print("입찰이 동률입니다. 경매가 무효 처리되어 카드 획득은 없습니다.")
        elif bid_player > bid_ai:
            # 플레이어가 낙찰 시 입찰 금액만큼 포인트 차감 및 카드 획득
            player.points -= bid_player
            player.add_card(Card(current_card))
            print(f"{player.name}가 {current_card} 카드를 낙찰 받았습니다!")
        else:
            # AI가 낙찰 시 입찰 금액만큼 포인트 차감 및 카드 획득
            ai.points -= bid_ai
            ai.add_card(Card(current_card))
            print(f"{ai.name}가 {current_card} 카드를 낙찰 받았습니다!")

        input("계속 진행하려면 엔터를 누르세요...")
