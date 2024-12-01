import pygame
import random
import time
import os
import sys

# リソースファイルのパスを取得する関数
def resource_path(relative_path):
    """PyInstallerの実行環境におけるリソースパスを取得する"""
    try:
        # PyInstallerでバンドルされた場合
        base_path = sys._MEIPASS
    except Exception:
        # 通常の実行環境の場合
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Pygameの初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 画像の読み込み
mentaiko_images = {
    "red": pygame.image.load(resource_path("mentaiko_red.png")),
    "silver": pygame.image.load(resource_path("mentaiko_silver.png")),
    "gold": pygame.image.load(resource_path("mentaiko_gold.png")),
    "rainbow": pygame.image.load(resource_path("mentaiko_rainbow.png"))
}

umeboshi_image = pygame.image.load(resource_path("umeboshi.png"))

try:
    background_image = pygame.image.load(resource_path("water_background.png"))
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Error loading background image: {e}")
    background_image = None

# 海老画像の読み込みと初期設定
ebi_original_image = pygame.image.load(resource_path("shrimp.png"))  # 元の海老画像を保存
ebi_image = pygame.transform.scale(ebi_original_image, (100, 100))  # 表示用の画像
ebi_rect = ebi_image.get_rect(center=(100, HEIGHT // 2))
ebi_speed = 5

# 明太子のクラス
class Mentaiko(pygame.sprite.Sprite):
    def __init__(self, color, points):
        super().__init__()
        self.image = pygame.transform.scale(mentaiko_images[color], (60, 60))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = random.randint(50, HEIGHT - 50)
        self.points = points
        self.speed = random.randint(2, 5)
        self.color = color

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# 梅干しのクラス
class Umeboshi(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(umeboshi_image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = random.randint(50, HEIGHT - 50)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# グループの初期化
mentaikos = pygame.sprite.Group()
umeboshis = pygame.sprite.Group()

# 海老サイズ効果の初期化
shrimp_enlarged = False
enlarged_start_time = 0

# 明太子を取った際に拡大を行う処理
if mentaiko_images == "rainbow":
    shrimp_enlarged = True
    enlarged_start_time = time.time()
    ebi_image = pygame.transform.scale(ebi_original_image, (200, 200))  # 拡大する
    ebi_rect = ebi_image.get_rect(center=ebi_rect.center)

# エフェクトの時間確認
if shrimp_enlarged and time.time() - enlarged_start_time > 5:
    reset_shrimp_size()  # 5秒経過したら元のサイズに戻す

# 元のサイズに戻す関数
def reset_shrimp_size():
    global ebi_image, ebi_rect, shrimp_enlarged
    ebi_image = pygame.transform.scale(ebi_original_image, (100, 100))  # 元のサイズに戻す
    ebi_rect = ebi_image.get_rect(center=ebi_rect.center)  # 位置も再調整
    shrimp_enlarged = False  # 拡大状態をリセット


# 重力の定義
gravity = 0.5  # 重力加速度（調整可能）

# メインゲームループ内
def main_game():
    global ebi_image, ebi_rect, shrimp_enlarged, enlarged_start_time  # グローバル変数を明示
    score = 0
    start_time = time.time()
    running = True

    # 海老の垂直速度を初期化
    ebi_speed_y = 0

    while running:
        screen.blit(background_image, (0, 0))

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # クリックで上昇
                ebi_speed_y = -10  # 上昇速度

        # 海老の重力による移動
        ebi_speed_y += gravity  # 自由落下を加速
        ebi_rect.y += ebi_speed_y

        # 画面外に出ないよう制限
        if ebi_rect.top < 0:
            ebi_rect.top = 0
            ebi_speed_y = 0
        if ebi_rect.bottom > HEIGHT:
            ebi_rect.bottom = HEIGHT
            ebi_speed_y = 0

        # 明太子生成
        if random.random() < 0.02:
            color_choice = random.choice(["red", "silver", "gold", "rainbow"])
            points_choice = {"red": 1, "silver": 3, "gold": 5, "rainbow": 0}
            mentaikos.add(Mentaiko(color_choice, points_choice[color_choice]))

        # 梅干し生成
        if random.random() < 0.01:
            umeboshis.add(Umeboshi())

        # 衝突判定
        for mentaiko in mentaikos:
            if ebi_rect.colliderect(mentaiko.rect):
                if mentaiko.color == "rainbow":
                    shrimp_enlarged = True
                    enlarged_start_time = time.time()
                    ebi_image = pygame.transform.scale(ebi_original_image, (200, 200))
                    ebi_rect = ebi_image.get_rect(center=ebi_rect.center)
                score += mentaiko.points
                mentaikos.remove(mentaiko)

        for umeboshi in umeboshis:
            if ebi_rect.colliderect(umeboshi.rect):
                score -= 10
                umeboshis.remove(umeboshi)

        # エフェクトの時間確認
        if shrimp_enlarged and time.time() - enlarged_start_time > 5:
            reset_shrimp_size()

        # 描画
        mentaikos.update()
        umeboshis.update()
        mentaikos.draw(screen)
        umeboshis.draw(screen)
        screen.blit(ebi_image, ebi_rect)

        # スコア表示
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # 残り時間表示
        elapsed_time = time.time() - start_time
        remaining_time = max(0, 60 - int(elapsed_time))
        timer_text = font.render(f"Time: {remaining_time}s", True, BLACK)
        screen.blit(timer_text, (WIDTH - 150, 10))

        if elapsed_time >= 60:
            return score

        pygame.display.update()
        clock.tick(30)


def end_screen(score):
    while True:
        screen.fill(WHITE)
        font = pygame.font.SysFont(None, 72)
        text = font.render("Finish!", True, BLACK)
        score_text = font.render(f"Your Score: {score}", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

        font = pygame.font.SysFont(None, 48)
        exit_text = font.render("Exit", True, BLACK)
        retry_text = font.render("1more", True, BLACK)
        exit_rect = pygame.Rect(WIDTH // 4, HEIGHT // 1.5, 150, 50)
        retry_rect = pygame.Rect(WIDTH * 3 // 4 - 150, HEIGHT // 1.5, 150, 50)
        pygame.draw.rect(screen, (200, 200, 200), exit_rect)
        pygame.draw.rect(screen, (200, 200, 200), retry_rect)
        screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width() // 2, exit_rect.centery - exit_text.get_height() // 2))
        screen.blit(retry_text, (retry_rect.centerx - retry_text.get_width() // 2, retry_rect.centery - retry_text.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    quit()
                if retry_rect.collidepoint(event.pos):
                    return

        pygame.display.update()
        clock.tick(30)

# ゲームの実行
while True:
    score = main_game()
    end_screen(score)
