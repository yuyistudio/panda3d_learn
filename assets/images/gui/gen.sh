if [ $# -eq 0 ]; then
    echo "usage: $0 output_name"
    exit -1
fi
name=$1

egg-texture-cards -o ${name}.egg -fps 30 `ls ${name}*.png`
