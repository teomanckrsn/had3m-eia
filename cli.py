"""HAD3M-EIA — Terminal (CLI) versiyonu. RAM tasarrufu için GUI olmadan çalışır."""

import os
import sys
import readline

from rag_engine import RAGEngine
from debate import debate, get_personality_names, persona_manager
from dev_team import DevProject, dev_team_work, get_team_roles, TEAM_ROLES
from model_config import detect_models, get_chat_model, get_vision_model
from file_manager import FileManager


CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


def print_banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════╗
║            HAD3M-EIA  (CLI)              ║
║     Yerel AI Asistan — Terminal Modu     ║
╚══════════════════════════════════════════╝{RESET}
""")


def print_help():
    print(f"""
{BOLD}Komutlar:{RESET}
  {GREEN}/sohbet{RESET}      Sohbet moduna geç (varsayılan)
  {GREEN}/tartisma{RESET}    Tartışma modu
  {GREEN}/kodla{RESET}       Geliştirme ekibi
  {GREEN}/dosya{RESET}       Dosya ekle/listele/temizle
  {GREEN}/tasi{RESET}        Dosya taşı
  {GREEN}/kisilik{RESET}     Kişilik listele/ekle
  {GREEN}/model{RESET}       Model bilgisi
  {GREEN}/yardim{RESET}      Bu menü
  {GREEN}/cik{RESET}         Çıkış

{DIM}Sohbet modunda direkt soru yazabilirsin.
Geri bildirim: cevaptan sonra + (beğen) veya - (beğenme) yaz.{RESET}
""")


def main():
    print_banner()
    print(f"{DIM}Modeller algılanıyor...{RESET}")

    config = detect_models()
    chat_model = config.get("chat_model", "?")
    vision_model = config.get("vision_model", "yok")
    print(f"{GREEN}Sohbet: {chat_model} | Görsel: {vision_model or 'yok'}{RESET}")

    print(f"{DIM}Engine başlatılıyor...{RESET}")
    engine = RAGEngine(on_status=lambda m: print(f"  {DIM}{m}{RESET}"))
    fm = FileManager(on_status=lambda m: print(f"  {DIM}{m}{RESET}"))
    print(f"{GREEN}Hazır!{RESET}")
    print_help()

    mode = "sohbet"
    last_question = ""
    last_answer = ""

    while True:
        try:
            if mode == "sohbet":
                prompt_text = f"{CYAN}[sohbet]>{RESET} "
            elif mode == "tartisma":
                prompt_text = f"{MAGENTA}[tartışma]>{RESET} "
            elif mode == "kodla":
                prompt_text = f"{GREEN}[kodla]>{RESET} "
            else:
                prompt_text = "> "

            user_input = input(prompt_text).strip()
            if not user_input:
                continue

            # Geri bildirim
            if user_input == "+" and last_answer:
                engine.feedback.add(last_question, last_answer, True)
                print(f"  {GREEN}👍 Beğeni kaydedildi!{RESET}")
                continue
            if user_input == "-" and last_answer:
                engine.feedback.add(last_question, last_answer, False)
                print(f"  {RED}👎 Beğenmeme kaydedildi!{RESET}")
                continue

            # Komutlar
            if user_input.startswith("/"):
                cmd = user_input.lower().split()[0]

                if cmd == "/cik":
                    print(f"{YELLOW}Görüşürüz!{RESET}")
                    break

                elif cmd == "/yardim":
                    print_help()

                elif cmd == "/sohbet":
                    mode = "sohbet"
                    print(f"{CYAN}Sohbet moduna geçildi.{RESET}")

                elif cmd == "/tartisma":
                    mode = "tartisma"
                    names = get_personality_names()
                    print(f"{MAGENTA}Tartışma modu.{RESET}")
                    print(f"Kişilikler: {', '.join(names)}")
                    print(f"Kullanım: {DIM}kişilik1 vs kişilik2: konu{RESET}")
                    print(f"Örnek: {DIM}Şirket Yöneticisi vs Finans Müdürü: Reklam bütçesi artırılmalı mı{RESET}")

                elif cmd == "/kodla":
                    mode = "kodla"
                    print(f"{GREEN}Geliştirme ekibi modu.{RESET}")
                    print(f"Roller: {', '.join(get_team_roles())}")
                    print(f"Kullanım: {DIM}proje_adı: görev açıklaması{RESET}")
                    print(f"Örnek: {DIM}web-site: Login sayfası yap responsive olsun{RESET}")

                elif cmd == "/dosya":
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        files = engine.get_indexed_files()
                        if files:
                            print(f"Yüklü dosyalar: {', '.join(files)}")
                        else:
                            print("Henüz dosya yüklenmedi.")
                        print(f"{DIM}/dosya ekle yol/dosya.pdf — dosya ekle{RESET}")
                        print(f"{DIM}/dosya temizle — tüm dosyaları temizle{RESET}")
                    else:
                        arg = parts[1].strip()
                        if arg == "temizle":
                            for f in engine.get_indexed_files():
                                engine.remove_document(f)
                            print("Tüm dosyalar temizlendi.")
                        elif arg.startswith("ekle "):
                            path = arg[5:].strip()
                            if os.path.exists(path):
                                engine.add_document(path)
                            else:
                                print(f"{RED}Dosya bulunamadı: {path}{RESET}")

                elif cmd == "/tasi":
                    parts = user_input.split(maxsplit=2)
                    if len(parts) < 3:
                        print(f"Kullanım: {DIM}/tasi kaynak hedef{RESET}")
                        print(f"Örnek: {DIM}/tasi ~/Desktop/rapor.pdf ~/Documents/{RESET}")
                    else:
                        result = fm.move_file(parts[1], parts[2])
                        icon = "✅" if result["success"] else "❌"
                        print(f"  {icon} {result['message']}")

                elif cmd == "/kisilik":
                    names = get_personality_names()
                    print(f"Kişilikler: {', '.join(names)}")

                elif cmd == "/model":
                    config = detect_models()
                    print(f"Kurulu modeller: {', '.join(config['installed_models'])}")
                    print(f"Sohbet: {config['chat_model']}")
                    print(f"Kod: {config['code_model']}")
                    print(f"Görsel: {config['vision_model'] or 'yok'}")

                else:
                    print(f"{RED}Bilinmeyen komut. /yardim yaz.{RESET}")
                continue

            # Mod bazlı işlem
            if mode == "sohbet":
                last_question = user_input
                print(f"  {DIM}Düşünüyor...{RESET}")
                answer = engine.ask(user_input)
                last_answer = answer
                print(f"\n{BOLD}AI:{RESET} {answer}\n")
                print(f"{DIM}  + beğen | - beğenme{RESET}")

            elif mode == "tartisma":
                # Format: kişilik1 vs kişilik2: konu
                if " vs " not in user_input or ":" not in user_input:
                    print(f"{RED}Format: kişilik1 vs kişilik2: konu{RESET}")
                    continue
                vs_part, topic = user_input.split(":", 1)
                p1, p2 = [x.strip() for x in vs_part.split(" vs ", 1)]
                topic = topic.strip()

                def on_msg(persona, msg):
                    print(f"\n{BOLD}{persona}:{RESET} {msg}")

                print(f"\n{MAGENTA}Tartışma: {p1} vs {p2} — {topic}{RESET}\n")
                debate(topic, p1, p2, rounds=2, on_message=on_msg)

            elif mode == "kodla":
                # Format: proje_adı: görev
                if ":" not in user_input:
                    print(f"{RED}Format: proje_adı: görev açıklaması{RESET}")
                    continue
                proj_name, task = user_input.split(":", 1)
                proj_name = proj_name.strip()
                task = task.strip()

                project = DevProject(proj_name, task)
                team = list(TEAM_ROLES.keys())

                def on_dev_msg(role, emoji, text, color):
                    print(f"\n{BOLD}{emoji} {role}:{RESET} {text}")

                print(f"\n{GREEN}Ekip çalışıyor: {', '.join(team)}{RESET}\n")
                dev_team_work(project, task, team, on_message=on_dev_msg)

        except KeyboardInterrupt:
            print(f"\n{YELLOW}Çıkmak için /cik yaz.{RESET}")
        except EOFError:
            break


if __name__ == "__main__":
    main()
