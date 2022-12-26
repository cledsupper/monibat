#!/data/data/com.termux/files/usr/bin/sh

if [ "$(id -u)" = "0" ];
  echo "NÃO EXECUTE COMO ROOT!"
  exit 1
fi

TARGET="$PREFIX/lib/MoniBat"
mkdir -p "$TARGET/config"
mkdir -p "$TARGET/data"

cp config/constants.py "$TARGET/config/"
cp config/tweaker.py "$TARGET/config/"
cp data/messages.py "$TARGET/data/"
cp driver.py "$TARGET/"
cp events.py "$TARGET/"
cp notify.py "$TARGET/"
cp eventloop.py "$TARGET/"
cp service.py "$TARGET/"

if [ ! -r "$HOME/.config/MoniBat/config.json" ]; then
  mkdir -p "$HOME/.config/MoniBat"
  cp samples/config.json "$HOME/.config/MoniBat/"
  echo "Defina a capacidade (em Ampère-hora/Ah) no arquivo: $HOME/.config/MoniBat/config.json"
 fi

mkdir -p "$HOME/.termux/boot"
cp moni.sh "$HOME/.termux/boot/"