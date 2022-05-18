mkdir -p ~/.streamlit

echo "[server]
headless = true
port = $PORT
enableCORS = false"  >> ~/.streamlit/config.toml

# echo "[server]
# headless = true
# port = $PORT
# enableCORS = false
# " > ~/.streamlit/config.toml