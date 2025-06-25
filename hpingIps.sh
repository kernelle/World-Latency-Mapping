while IFS= read -r ip; do
    echo "$ip" >> rtts.txt
    sudo hping3 -S -c 1 -p 80 "$ip" >> rtts.txt
done < IPList.txt 
