import socket
import json
import threading
import time
from game_logic import GameLogic
from player import Player
from auction import Auction

class GameServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 타임아웃 설정 추가
        self.server.settimeout(1.0)
        try:
            self.server.bind((host, port))
            self.server.listen(2)
            self.clients = []
            self.player_names = []
            self.running = True  # 서버 실행 상태 플래그
            print(f"서버가 {host}:{port}에서 시작되었습니다.")
            # 현재 서버의 IP 주소 출력
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"서버 IP 주소: {local_ip}")
        except Exception as e:
            print(f"서버 시작 오류: {e}")
            raise e

    def start(self):
        """서버 시작 및 클라이언트 연결 대기"""
        print("클라이언트 연결 대기 중...")
        try:
            while self.running and len(self.clients) < 2:
                try:
                    client_socket, address = self.server.accept()
                    # 클라이언트 소켓에도 타임아웃 설정
                    client_socket.settimeout(5.0)
                    
                    # 클라이언트 연결 처리를 별도 스레드로 실행
                    client_thread = threading.Thread(
                        target=self.handle_client_connection,
                        args=(client_socket, address)
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"클라이언트 연결 처리 중 오류 발생: {e}")
                    continue
                    
        except Exception as e:
            print(f"서버 실행 중 오류 발생: {e}")
        finally:
            self.cleanup()

    def handle_client_connection(self, client_socket, address):
        """클라이언트 연결 처리"""
        try:
            # 클라이언트로부터 플레이어 이름 받기
            player_name = client_socket.recv(1024).decode()
            if not player_name:
                raise ConnectionError("플레이어 이름을 받지 못했습니다.")
                
            self.clients.append(client_socket)
            self.player_names.append(player_name)
            
            print(f"플레이어 {player_name}가 접속했습니다. ({address})")
            print(f"현재 접속자 수: {len(self.clients)}/2")
            
            # 두 번째 플레이어가 접속하면 게임 시작
            if len(self.clients) == 2:
                self.start_game()
                
        except Exception as e:
            print(f"클라이언트 {address} 처리 중 오류 발생: {e}")
            self.remove_client(client_socket)

    def remove_client(self, client_socket):
        """클라이언트 연결 제거"""
        try:
            if client_socket in self.clients:
                idx = self.clients.index(client_socket)
                self.clients.remove(client_socket)
                self.player_names.pop(idx)
                client_socket.close()
        except:
            pass

    def cleanup(self):
        """서버 및 연결된 소켓들을 정리"""
        print("\n서버 정리 중...")
        self.running = False
        
        # 모든 클라이언트 연결 종료
        for client in self.clients[:]:  # 복사본으로 반복
            self.remove_client(client)
            
        # 서버 소켓 종료
        try:
            self.server.close()
        except:
            pass
        print("서버가 종료되었습니다.")

    def send_to_client(self, client_socket, message):
        """안전한 메시지 전송"""
        try:
            client_socket.send(message.encode())
            return True
        except Exception as e:
            print(f"메시지 전송 실패: {e}")
            self.remove_client(client_socket)
            return False

    def start_game(self):
        """게임 시작 및 진행"""
        try:
            # 각 플레이어에게 상대방 정보 전송
            for i in range(2):
                opponent_name = self.player_names[1-i]
                if not self.send_to_client(self.clients[i], f"OPPONENT:{opponent_name}"):
                    return

            # 경매 페이즈 시작
            self.auction_phase()
            
        except Exception as e:
            print(f"게임 시작 중 오류 발생: {e}")
            self.cleanup()

    def auction_phase(self):
        """경매 페이즈 진행"""
        auction = Auction()
        player1_points = 1000
        player2_points = 1000
        
        while player1_points >= 100 or player2_points >= 100:
            try:
                current_card = auction.get_current_card()
                
                # 현재 카드 정보 전송
                for client in self.clients:
                    if not self.send_to_client(client, f"AUCTION_CARD:{current_card.name}"):
                        return

                # 입찰가 수집
                bids = []
                for i, client in enumerate(self.clients):
                    try:
                        bid_data = client.recv(1024).decode()
                        if not bid_data:
                            raise ConnectionError(f"플레이어 {i+1}의 연결이 끊겼습니다.")
                        bid = int(bid_data.split(":")[1])
                        bids.append(bid)
                    except Exception as e:
                        print(f"입찰가 수집 중 오류 발생: {e}")
                        return

                # 승자 결정 및 포인트 차감
                winner_idx = 0 if bids[0] > bids[1] else 1
                if winner_idx == 0:
                    player1_points -= bids[0]
                else:
                    player2_points -= bids[1]

                # 결과 전송
                for i, client in enumerate(self.clients):
                    result = "WIN" if i == winner_idx else "LOSE"
                    if not self.send_to_client(client, f"AUCTION_RESULT:{result}:{bids[winner_idx]}"):
                        return

            except Exception as e:
                print(f"경매 진행 중 오류 발생: {e}")
                return

        # 배틀 페이즈로 전환
        self.battle_phase()

    def battle_phase(self):
        """배틀 페이즈 진행"""
        # 플레이어들의 카드 정보 초기화
        player1_cards = ["가위", "바위", "보"] * 2
        player2_cards = ["가위", "바위", "보"] * 2

        while player1_cards and player2_cards:
            try:
                # 각 플레이어에게 상대방의 카드 정보와 함께 배틀 시작 알림
                if not (self.send_to_client(self.clients[0], f"BATTLE_START:TURN:{','.join(player2_cards)}") and
                       self.send_to_client(self.clients[1], f"BATTLE_START:TURN:{','.join(player1_cards)}")):
                    return

                # 각 플레이어의 카드 선택 받기
                cards = []
                for i, client in enumerate(self.clients):
                    try:
                        card_data = client.recv(1024).decode()
                        if not card_data:
                            raise ConnectionError(f"플레이어 {i+1}의 연결이 끊겼습니다.")
                        cards.append(card_data.split(":")[1])
                    except Exception as e:
                        print(f"카드 선택 수집 중 오류 발생: {e}")
                        return

                # 승패 판정
                result = self.determine_winner(cards[0], cards[1])
                
                # 결과에 따라 카드 제거
                if result == "P1_WIN":
                    player2_cards.remove(cards[1])
                elif result == "P2_WIN":
                    player1_cards.remove(cards[0])
                
                # 결과 전송
                if not (self.send_to_client(self.clients[0], 
                                          f"BATTLE_RESULT:{result}:{cards[0]}:{cards[1]}:{','.join(player2_cards)}") and
                       self.send_to_client(self.clients[1], 
                                          f"BATTLE_RESULT:{result}:{cards[1]}:{cards[0]}:{','.join(player1_cards)}")):
                    return

            except Exception as e:
                print(f"배틀 진행 중 오류 발생: {e}")
                return

        # 게임 종료
        winner = "Player 2" if not player1_cards else "Player 1"
        for client in self.clients:
            self.send_to_client(client, f"GAME_OVER:{winner}")

    def determine_winner(self, card1, card2):
        """가위바위보 승패 판정"""
        if card1 == card2:
            return "TIE"
        elif ((card1 == "가위" and card2 == "보") or
              (card1 == "바위" and card2 == "가위") or
              (card1 == "보" and card2 == "바위")):
            return "P1_WIN"
        else:
            return "P2_WIN"

if __name__ == "__main__":
    try:
        server = GameServer()
        server.start()
    except KeyboardInterrupt:
        print("\n서버가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}") 