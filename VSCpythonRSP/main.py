# main.py
import os
import time
from auction import Auction
from player import create_player, Player
from game_logic import GameLogic

def clear_console():
    """콘솔 화면 정리 함수 (OS별: 'cls' 또는 'clear')"""
    os.system("cls" if os.name == "nt" else "clear")

def main():
    clear_console()
    print("🎮 가위바위보 경매 게임 시작! 🎮")
    time.sleep(1)
    
    # 플레이어 생성
    player1 = create_player()
    player2 = Player("AI 상대")
    
    # 경매 시스템 초기화
    auction_system = Auction()
    
    # 게임 로직 객체 생성
    game = GameLogic(player1, player2, auction_system)
    
    # 경매 페이즈 진행 (실시간 포인트 업데이트)
    while game.can_continue_auction():
        clear_console()
        game.auction_phase()
        time.sleep(2)
    
    # 배틀 페이즈 진행 (카드가 0장이 될 때까지)
    clear_console()
    game.battle_phase()
    
    # 게임 종료 및 최종 결과 출력
    clear_console()
    game.end_phase()

if __name__ == "__main__":
    main()
