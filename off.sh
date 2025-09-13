prev=$(find /workspace/ComfyUI/output -type f -exec stat -c '%W %n' {} + | sort -k1,1nr | head -n 1 | cut -d' ' -f2-)
counter=0
while true; do
  sleep 60
  current=$(find /workspace/ComfyUI/output -type f -exec stat -c '%W %n' {} + | sort -k1,1nr | head -n 1 | cut -d' ' -f2-)
  if [ "$current" = "$prev" ]; then
    counter=$((counter + 1))
  else
    prev="$current"
    counter=0
  fi
  if [ $counter -ge 1 ]; then
    runpodctl remove pod $RUNPOD_POD_ID
    exit 0
  fi
done
