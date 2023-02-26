#!/data/data/com.termux/files/usr/bin/sh

if [ "$(id -u)" = "0" ]; then
  echo "NÃO EXECUTE COMO ROOT!"
  exit 1
fi

echo "Instalação de dependências"
pip install -r DEPS.txt

echo "Instalação do serviço"
TARGET="$PREFIX/lib/MoniBat"
mkdir -p "$TARGET/config"
mkdir -p "$TARGET/data"

cp config/constants.py "$TARGET/config/"
cp config/tweaker.py "$TARGET/config/"
cp data/messages.py "$TARGET/data/"
cp batteryinterface.py "$TARGET/"
cp batteryemulator.py "$TARGET/"
cp batterydriver.py "$TARGET/"
cp events.py "$TARGET/"
cp notify.py "$TARGET/"
cp eventloop.py "$TARGET/"
cp service.py "$TARGET/"
chmod +x "$TARGET/service.py"

if [ ! -r "$HOME/.config/MoniBat/config.json" ]; then
  mkdir -p "$HOME/.config/MoniBat"
  cp samples/config.json "$HOME/.config/MoniBat/"
  echo "Defina a capacidade (em Ampère-hora/Ah) no arquivo: $HOME/.config/MoniBat/config.json"
 fi

mkdir -p "$HOME/.termux/boot"
cp moni.sh "$HOME/.termux/boot/"
rm "$PREFIX/bin/monibat.run"
ln -s "$TARGET/service.py" "$PREFIX/bin/monibat.run"

rm "$TARGET/driver.py"
