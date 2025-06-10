# game_logic.py
import os
import time
from cards import Card
from auction import Auction

class GameLogic:
    """
    게임 로직 클래스
    - 경매 페이즈에서는 경매에 올라온 카드와 실시간 포인트 변화를 관리합니다.
    - 배틀 페이즈에서는 가위바위보로 대결하고, 진 쪽의 카드만 삭제합니다.
    - 게임 종료 시 최종 카드 목록과 포인트 상태를 출력합니다.
    """
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.is_auction_active = True

    def clear_console(self):
        """운영체제에 맞춰 콘솔 화면을 클리어합니다."""
        os.system("cls" if os.name == "nt" else "clear")

    def display_player_cards(self, player):
        """플레이어가 보유한 카드 목록과 남은 카드 개수를 출력합니다."""
        print(f"\n📜 {player.name}의 남은 카드:")
        card_names = [card.name for card in player.cards]
        print(f"🃏 카드 목록: {', '.join(card_names) if card_names else '없음'}")
        print(f"🔢 남은 카드 개수: {len(player.cards)}")

    def display_player_points(self):
        """실시간으로 플레이어의 포인트 상태를 출력합니다."""
        print("\n💰 현재 포인트 상태:")
        print(f"{self.player1.name}: {self.player1.points} 포인트")
        print(f"{self.player2.name}: {self.player2.points} 포인트")

    def can_continue_auction(self):
        """
        경매 진행 가능 여부:
        두 플레이어 중 어느 한 쪽이라도 100 포인트 이상 있다면 경매를 계속 진행할 수 있습니다.
        """
        return self.is_auction_active and (self.player1.points >= 100 or self.player2.points >= 100)

    def auction_phase(self):
        """
        경매 페이즈:
         - 매 경매 전, 현재 포인트 상태를 출력하고,
         - Auction.collect_bids() 메서드를 통해 경매를 진행합니다.
         - 입찰이 끝난 후 실시간 업데이트된 포인트를 보여주며,
         - 플레이어 중 한 쪽이라도 100포인트 미만이면 경매 페이즈를 종료합니다.
        """
        while self.can_continue_auction():
            self.clear_console()
            print("\n🎴 경매 시작! 현재 포인트:")
            self.display_player_points()

            # 경매 진행 (입찰 시 카드가 공개되고, 플레이어와 AI의 입찰을 처리)
            self.auction_system.collect_bids(self.player1, self.player2)

            self.clear_console()
            print("\n🏆 입찰 후 남은 포인트:")
            self.display_player_points()

            if self.player1.points < 100 and self.player2.points < 100:
                print("\n🏁 모든 플레이어가 입찰할 포인트가 부족합니다! 경매 종료.")
                self.is_auction_active = False

            time.sleep(2)

    def battle_phase(self):
        """
        배틀 페이즈:
         - 경매 페이즈 종료 후 진행되며, 각 플레이어의 카드가 0장이 될 때까지 진행됩니다.
         - 가위바위보 대결 시, 무승부 → 양쪽 모두 카드 유지,
           승리한 쪽에 따라 패배한 쪽의 카드만 삭제됩니다.
        """
        self.clear_console()
        print("\n⚔️ 배틀 페이즈 시작! 카드가 0장이 될 때까지 대결을 진행합니다.")
        self.display_player_cards(self.player1)
        self.display_player_cards(self.player2)

        while self.player1.cards and self.player2.cards:
            action = input("배틀 진행하려면 '예'를 입력하세요 (중단하려면 '아니요'): ")
            if action.lower() == "아니요":
                print("\n🏁 배틀 종료!")
                break
            self.play_turn()

    def play_turn(self):
        """
        한 턴 진행:
         - 플레이어와 AI가 각각 보유한 카드 중 하나씩 선택하여 가위바위보 대결을 합니다.
         - 승리 결과에 따라, 진 쪽의 카드만 삭제합니다.
         - 무승부 시에는 양쪽 모두 카드를 유지합니다.
        """
        self.clear_console()
        print(f"\n⚔️ {self.player1.name} vs {self.player2.name} 카드 대결!")
        
        # 플레이어 카드 목록 표시
        self.display_player_cards(self.player1)
        card_choice_p1 = input(f"{self.player1.name}, 사용할 카드를 입력하세요 (가위, 바위, 보): ")
        card1 = next((card for card in self.player1.cards if card.name == card_choice_p1), None)

        # AI는 보유 카드 중 첫 번째를 선택합니다.
        card2 = self.player2.cards[0] if self.player2.cards else None

        if card1 is None or card2 is None:
            print("\n🚨 잘못된 카드 선택이거나, 상대방이 카드가 없습니다. 이번 턴을 무효 처리합니다.")
            input("계속하려면 엔터를 누르세요...")
            return

        print(f"\n{self.player1.name}의 카드: {card1.name}")
        print(f"{self.player2.name}의 카드: {card2.name}")

        # 승패 결과 결정 (반환값: 'tie', 'player1', 'player2')
        result = self.determine_winner(card1, card2)
        if result == 'tie':
            print("\n🔄 무승부입니다! 양쪽 모두 카드를 유지합니다.")
        elif result == 'player1':
            print(f"\n🏆 {self.player1.name} 승리! {self.player2.name}의 카드가 삭제됩니다.")
            self.player2.cards.remove(card2)
        elif result == 'player2':
            print(f"\n🏆 {self.player2.name} 승리! {self.player1.name}의 카드가 삭제됩니다.")
            self.player1.cards.remove(card1)

        input("이번 턴 종료. 엔터를 눌러 계속 진행...")

    def determine_winner(self, card1, card2):
        """
        가위바위보 승패 판정:
        - 두 카드를 비교하여 승자를 결정합니다.
        - 무승부 시 'TIE', 플레이어1 승리 시 'P1_WIN', 플레이어2 승리 시 'P2_WIN' 반환
        """
        if card1.name == card2.name:
            return 'TIE'
        elif ((card1.name == "가위" and card2.name == "보") or
              (card1.name == "바위" and card2.name == "가위") or
              (card1.name == "보" and card2.name == "바위")):
            return 'P1_WIN'
        else:
            return 'P2_WIN'

    def end_phase(self):
        """
        게임 종료:
         - 최종 카드 목록과 포인트 상태를 출력합니다.
         - 보유 카드가 0장이 된 플레이어가 패배하며, 승리자가 결정됩니다.
        """
        self.clear_console()
        print("\n🏁 게임 종료! 최종 카드 목록:")
        self.display_player_cards(self.player1)
        self.display_player_cards(self.player2)
        print("\n🏆 최종 포인트 상태:")
        self.display_player_points()

        if self.is_game_over():
            print(self.get_game_result())
        input("엔터를 눌러 종료...")

    def is_game_over(self):
        """게임 종료 조건 확인"""
        return len(self.player1.cards) == 0 or len(self.player2.cards) == 0

    def get_game_result(self):
        """게임 결과 반환"""
        if len(self.player1.cards) == 0:
            return f"{self.player2.name} 승리!"
        else:
            return f"{self.player1.name} 승리!"
