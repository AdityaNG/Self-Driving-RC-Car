git fetch --all
git reset --hard origin/master
git pull

chmod +x update.sh OnBoot.sh
cd bluetooth
chmod +x start.sh start_back.sh stop.sh bluetooth_connect.sh reset.sh start_no_threads.sh
cd ../web
chmod +x start.sh stop.sh