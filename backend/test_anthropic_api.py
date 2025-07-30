#!/usr/bin/env python3
"""
Anthropic API接続テストスクリプト
"""

import os
from anthropic import Anthropic
from config import settings

def test_anthropic_connection():
    """Anthropic APIへの接続をテストする"""
    
    print("=== Anthropic API接続テスト ===")
    
    # 設定の確認
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key or api_key == "sk-ant-api03-...":
        print("❌ エラー: ANTHROPIC_API_KEYが正しく設定されていません")
        print("以下の手順でAPIキーを設定してください：")
        print("1. https://console.anthropic.com/ にアクセス")
        print("2. APIキーを生成")
        print("3. config.pyで直接設定")
        return False
    
    print(f"✅ APIキー設定確認: {api_key[:10]}...")
    
    try:
        # Anthropicクライアントの初期化
        client = Anthropic(api_key=api_key)
        print("✅ Anthropicクライアント初期化成功")
        
        # 簡単なテストメッセージを送信
        print("📤 テストメッセージを送信中...")
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "こんにちは！これはテストメッセージです。"
                }
            ]
        )
        
        print("✅ API接続成功！")
        print(f"📥 レスポンス: {message.content[0].text}")
        
        return True
        
    except Exception as e:
        print(f"❌ API接続エラー: {str(e)}")
        
        if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            print("💡 解決方法: APIキーが無効です。新しいAPIキーを生成してください。")
        elif "rate limit" in str(e).lower():
            print("💡 解決方法: レート制限に達しました。しばらく待ってから再試行してください。")
        elif "not_found_error" in str(e).lower():
            print("💡 解決方法: モデル名が無効です。利用可能なモデルを確認してください。")
        else:
            print("💡 解決方法: ネットワーク接続またはAPIキーの設定を確認してください。")
        
        return False

def main():
    """メイン関数"""
    try:
        result = test_anthropic_connection()
        if result:
            print("\n🎉 Anthropic API接続テスト完了！")
        else:
            print("\n⚠️  API接続テスト失敗")
            exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  テストを中断しました")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {str(e)}")

if __name__ == "__main__":
    main() 