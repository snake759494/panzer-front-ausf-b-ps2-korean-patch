# 백그라운드 조작: run.sh [ISO|""] "키들" 접두어   (키: 16진 VK, wN 대기, s 캡처, q 종료)
E="powershell -ExecutionPolicy Bypass -File $(dirname "$0")/emu2.ps1"
iso="$1"; keys="$2"; pre="$3"; n=0
if [ -n "$iso" ]; then $E stop >/dev/null; $E start "$iso" >/dev/null; fi
for k in $keys; do
 case $k in w*) sleep ${k#w};; s) $E shot "$pre$n.png" >/dev/null; echo "$pre$n.png"; n=$((n+1));; q) $E stop >/dev/null;; *) $E key $k,150 >/dev/null; sleep 1;; esac
done
