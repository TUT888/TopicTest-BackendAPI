# Backend API for Mobile Application
Backend API source code for Task 6.1D

## How to run
1. Clone this repo
2. Install required dependencies. Detailed instruction refer to [sit3057082025/BackendApiLLM_T6.1D](https://github.com/sit3057082025/BackendApiLLM_T6.1D?tab=readme-ov-file#instructions)
3. Create `.env` file with following information
    ```
    API_TOKEN=<Your generated token>
    API_URL=https://router.huggingface.co/nebius/v1/chat/completions
    MODEL=google/gemma-2-2b-it
    ```
4. Run the files
    ```
    python main_api.py
    ```
5. Use the IP address shown on your terminal for Android Application
    - Use IP on your local network (Ex: `http://192.168.0.1`)
    - **Avoid using loop back addresss** (Ex: `localhost` or `http://127.0.0.1`) because Android Virtual Devices can not access to this kind address on our computer

## Reference
Model and inference used in project
- LLM model: [google/gemma-2-2b-it](https://huggingface.co/google/gemma-2-2b-it)
- Nebius provider: [Nebius AI Studio Documentation](https://docs.nebius.com/studio/api/examples)
- Color reference [Scheme Color - Shiny Light Blue Color Scheme](https://www.schemecolor.com/shiny-light-blue.php)

Other:
- About inference provider: [Inference Provider](https://huggingface.co/docs/inference-providers/en/index)
- Search model by inference provider: [Hugging Face - Inference Providers](https://huggingface.co/models?other=conversational&sort=likes)