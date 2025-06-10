import socket
import json
import os
import time
import random
import threading

class GameClient:
    def __init__(self, host=None, port=5000):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.points = 1000  # 초기 포인트
        self.cards = []     # 보유 카드
        self.opponent_cards = []  # 상대방 카드
        self.is_ai_mode = False  # AI 모드 여부
        self.running = True  # 클라이언트 실행 상태
        self.opponent_name = ""  # 상대방 이름

    def connect(self):
        """서버에 연결"""
        # 게임 모드 선택
        self.clear_console()
        print("\n=== 가위바위보 경매 게임 ===")
        print("\n게임 모드를 선택하세요:")
        print("1. AI 대전")
        print("2. 플레이어 대전")
        
        while True:
            mode = input("선택 (1 또는 2): ")
            if mode in ['1', '2']:
                self.is_ai_mode = (mode == '1')
                break
            print("잘못된 입력입니다. 1 또는 2를 입력하세요.")

        if self.is_ai_mode:
            print("\nAI 대전 모드를 시작합니다...")
            self.start_ai_mode()
            return

        if self.host is None:
            self.host = input("서버 IP 주소를 입력하세요: ")
        
        max_attempts = 3
        current_attempt = 0
        
        while current_attempt < max_attempts and self.running:
            try:
                print(f"\n서버 연결 시도 중... ({current_attempt + 1}/{max_attempts})")
                print(f"연결 대상: {self.host}:{self.port}")
                
                self.client.settimeout(5.0)  # 연결 타임아웃 설정
                self.client.connect((self.host, self.port))
                print(f"서버에 연결되었습니다. ({self.host}:{self.port})")
                
                # 플레이어 이름 입력 및 전송
                player_name = input("플레이어 이름을 입력하세요: ")
                self.send_message(f"PLAYER:{player_name}")
                
                # 상대방 정보 수신
                print("상대방 정보 대기 중...")
                opponent_data = self.receive_message()
                if opponent_data.startswith("OPPONENT:"):
                    self.opponent_name = opponent_data.split(":")[1]
                    print(f"상대방 플레이어: {self.opponent_name}")
                else:
                    raise ConnectionError("잘못된 상대방 정보를 받았습니다.")
                
                # 게임 루프 시작
                self.game_loop()
                break
                
            except ConnectionRefusedError:
                print(f"\n연결이 거부되었습니다. 서버가 실행 중인지 확인해주세요.")
                print("가능한 문제:")
                print("1. 서버가 실행되지 않았을 수 있습니다.")
                print("2. 입력한 IP 주소가 올바르지 않을 수 있습니다.")
                print("3. 방화벽이 연결을 차단했을 수 있습니다.")
                
            except socket.timeout:
                print("\n연결 시도 시간이 초과되었습니다.")
                
            except Exception as e:
                print(f"\n연결 오류: {e}")
                print("\n문제 해결 방법:")
                print("1. 서버가 실행 중인지 확인하세요.")
                print("2. 입력한 IP 주소가 올바른지 확인하세요.")
                print("3. 방화벽 설정을 확인하세요.")
                print("4. 네트워크 연결을 확인하세요.")
            
            if current_attempt < max_attempts - 1:
                retry = input("\n다시 시도하시겠습니까? (y/n): ")
                if retry.lower() != 'y':
                    break
                self.host = input("서버 IP 주소를 다시 입력하세요 (이전과 같다면 Enter): ") or self.host
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            current_attempt += 1
        
        if current_attempt >= max_attempts:
            print("\n최대 연결 시도 횟수를 초과했습니다.")
            print("프로그램을 종료합니다.")

    def send_message(self, message):
        """안전한 메시지 전송"""
        try:
            self.client.send(message.encode())
            return True
        except Exception as e:
            print(f"메시지 전송 실패: {e}")
            return False

    def receive_message(self):
        """안전한 메시지 수신"""
        try:
            data = self.client.recv(1024).decode()
            if not data:
                raise ConnectionError("서버와의 연결이 끊어졌습니다.")
            return data
        except Exception as e:
            print(f"메시지 수신 실패: {e}")
            raise

    def game_loop(self):
        """게임 진행"""
        try:
            while self.running:
                data = self.receive_message()
                if not data:
                    break
                
                cmd = data.split(":")[0]
                
                if cmd == "AUCTION_CARD":
                    self.handle_auction(data)
                elif cmd == "BATTLE_START":
                    self.handle_battle(data)
                elif cmd == "GAME_OVER":
                    self.handle_game_over(data)
                    break
                
        except ConnectionError:
            print("\n서버와의 연결이 끊어졌습니다.")
        except Exception as e:
            print(f"\n게임 진행 중 오류 발생: {e}")
        finally:
            self.cleanup()

    def handle_auction(self, data):
        """경매 처리"""
        try:
            card_name = data.split(":")[1]
            self.clear_console()
            print(f"\n🎴 현재 경매 카드: {card_name}")
            print(f"💰 보유 포인트: {self.points}")
            
            while True:
                try:
                    bid = int(input("입찰가를 입력하세요 (0은 포기): "))
                    if 0 <= bid <= self.points:
                        break
                    print("잘못된 입력입니다. 보유 포인트 이하의 값을 입력하세요.")
                except ValueError:
                    print("숫자를 입력해주세요.")
            
            # 입찰가 전송
            if not self.send_message(f"BID:{bid}"):
                return
            
            # 경매 결과 수신
            result_data = self.receive_message()
            if not result_data.startswith("AUCTION_RESULT:"):
                raise ValueError("잘못된 경매 결과 형식입니다.")
                
            result, winning_bid = result_data.split(":")[1:]
            
            if result == "WIN":
                self.points -= int(winning_bid)
                self.cards.append(card_name)
                print(f"\n🎉 경매 승리! {card_name} 카드를 획득했습니다.")
            else:
                print("\n😢 경매에서 패배했습니다.")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"경매 처리 중 오류 발생: {e}")
            raise

    def handle_battle(self, data):
        """배틀 페이즈 처리"""
        try:
            # 상대방 카드 정보 업데이트
            opponent_cards = data.split(":")[2].split(",")
            self.opponent_cards = opponent_cards
            
            self.clear_console()
            print("\n⚔️ 배틀 페이즈 시작!")
            print(f"\n{self.opponent_name}의 보유 카드:", ", ".join(self.opponent_cards))
            print("내 보유 카드:", ", ".join(self.cards))
            
            while True:
                card_choice = input("\n사용할 카드를 선택하세요 (가위/바위/보): ")
                if card_choice in self.cards:
                    break
                print("보유하지 않은 카드입니다.")
            
            # 선택한 카드 전송
            if not self.send_message(f"CARD:{card_choice}"):
                return
            
            # 결과 수신
            result_data = self.receive_message()
            if not result_data.startswith("BATTLE_RESULT:"):
                raise ValueError("잘못된 대결 결과 형식입니다.")
                
            result, my_card, opponent_card, opponent_cards = result_data.split(":")
            self.opponent_cards = opponent_cards.split(",")
            
            print(f"\n🎴 나의 카드: {my_card}")
            print(f"🎴 상대방 카드: {opponent_card}")
            
            if result == "TIE":
                print("\n🔄 무승부!")
            elif result == "WIN":
                print("\n🎉 승리!")
                if opponent_card in self.opponent_cards:
                    self.opponent_cards.remove(opponent_card)
            else:
                print("\n😢 패배...")
                if my_card in self.cards:
                    self.cards.remove(my_card)
            
            time.sleep(2)
            
        except Exception as e:
            print(f"배틀 처리 중 오류 발생: {e}")
            raise

    def handle_game_over(self, data):
        """게임 종료 처리"""
        try:
            result = data.split(":")[1]
            self.clear_console()
            print("\n🏁 게임 종료!")
            print(f"결과: {result}")
            print(f"최종 보유 카드: {', '.join(self.cards)}")
            print(f"남은 포인트: {self.points}")
            
        except Exception as e:
            print(f"게임 종료 처리 중 오류 발생: {e}")
            raise

    def cleanup(self):
        """연결 정리"""
        self.running = False
        try:
            self.client.close()
        except:
            pass

    def clear_console(self):
        """콘솔 화면 정리"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def start_ai_mode(self):
        """AI 대전 모드 실행"""
        self.opponent_cards = ["가위", "바위", "보"] * 2  # AI의 초기 카드
        print("\n=== AI 대전 모드 ===")
        print("당신의 초기 포인트:", self.points)
        
        # 경매 페이즈
        while self.points >= 100:
            self.handle_ai_auction()
        
        # 배틀 페이즈
        while self.cards and self.opponent_cards:
            self.handle_ai_battle()
        
        # 게임 종료
        self.handle_ai_game_over()

    def handle_ai_auction(self):
        """AI 대전 모드의 경매 처리"""
        self.clear_console()
        card = random.choice(["가위", "바위", "보"])
        print(f"\n🎴 현재 경매 카드: {card}")
        print(f"💰 보유 포인트: {self.points}")
        
        while True:
            try:
                bid = int(input("입찰가를 입력하세요 (0은 포기): "))
                if 0 <= bid <= self.points:
                    break
                print("잘못된 입력입니다. 보유 포인트 이하의 값을 입력하세요.")
            except ValueError:
                print("숫자를 입력해주세요.")
        
        # AI의 입찰가 결정 (랜덤하게 결정)
        ai_bid = random.randint(0, min(self.points, 300))
        print(f"\nAI의 입찰가: {ai_bid}")
        
        if bid > ai_bid:
            self.points -= bid
            self.cards.append(card)
            print(f"\n🎉 경매 승리! {card} 카드를 획득했습니다.")
        else:
            print("\n😢 경매에서 패배했습니다.")
            self.opponent_cards.append(card)
        
        time.sleep(2)

    def handle_ai_battle(self):
        """AI 대전 모드의 배틀 처리"""
        self.clear_console()
        print("\n⚔️ 배틀 페이즈")
        print("\n내 카드:", ", ".join(self.cards))
        print("AI의 남은 카드 수:", len(self.opponent_cards))
        print("AI의 보유 카드:", ", ".join(self.opponent_cards))  # AI의 카드도 표시
        
        while True:
            card_choice = input("\n사용할 카드를 선택하세요 (가위/바위/보): ")
            if card_choice in self.cards:
                break
            print("보유하지 않은 카드입니다.")
        
        # AI의 카드 선택
        ai_card = random.choice(self.opponent_cards)
        
        print(f"\n🎴 나의 카드: {card_choice}")
        print(f"🎴 AI의 카드: {ai_card}")
        
        # 승패 판정
        result = self.determine_winner(card_choice, ai_card)
        
        if result == "TIE":
            print("\n🔄 무승부!")
        elif result == "WIN":
            print("\n🎉 승리!")
            self.opponent_cards.remove(ai_card)
        else:
            print("\n😢 패배...")
            self.cards.remove(card_choice)
        
        time.sleep(2)

    def determine_winner(self, card1, card2):
        """가위바위보 승패 판정"""
        if card1 == card2:
            return "TIE"
        elif ((card1 == "가위" and card2 == "보") or
              (card1 == "바위" and card2 == "가위") or
              (card1 == "보" and card2 == "바위")):
            return "WIN"
        else:
            return "LOSE"

    def handle_ai_game_over(self):
        """AI 대전 모드의 게임 종료 처리"""
        self.clear_console()
        print("\n🏁 게임 종료!")
        if not self.opponent_cards:
            print("🎉 축하합니다! AI를 물리쳤습니다!")
        else:
            print("😢 AI에게 패배했습니다.")
        print(f"\n최종 보유 카드: {', '.join(self.cards)}")
        print(f"남은 포인트: {self.points}")

if __name__ == "__main__":
    try:
        client = GameClient()
        client.connect()
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    finally:
        if 'client' in locals():
            client.cleanup() 