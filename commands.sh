# Run via their script
./scripts/comp-run.py data/ double_src/bin/ ratio-gpu-compress

# Run directly
./double_src/ratio-gpu-compress data/double/city_temperature_f.bin data/double/compressed/city_temperature_f.comp y
./double_src/ratio-gpu-decompress data/double/compressed/city_temperature_f.comp data/double/decompressed/city_temperature_f.decomp y

