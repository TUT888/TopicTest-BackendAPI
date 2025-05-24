# Backend API for Mobile Application
Backend API source code for Task 10.1D, **extended from** [Task 6.1D - Backend](https://github.com/alice-tat/Task6_1D_BackendAPI)

This backend API **support the Android Application** at [Task 10.1D - Android Application](https://github.com/alice-tat/Task10_1D_ImprovedPersonalizedLearningExperiencesApp)

## Changes in this project
After cloning previous project (Task 6.1D), some changes were added to this backend repository.
### Endpoints of MongoDB interaction
- Student-related endpoints:
    - **[GET] /share_profile**: an endpoint for profile sharing purpose, which will render student profile with their achievement
    - **[POST] /students**: an endpoint for adding new student to database
    - **[POST] /students/login**: an endpoint for checking existing student
- Task-related endpoints:
    - **[POST] /tasks**: an endpoint for adding new task
    - **[PUT] /tasks/id**: an endpoint for updating task detail
    - **[GET] /tasks**: an endpoint for getting available/finished tasks for specific student
    - **[DELETE] /tasks/id**: an endpoint for deleting a task

### Endpoints of AI-powered API
The application extended the AI-generated quizzes with AI profile summary feature from backedn server.
- **[GET] /getQuiz**: an endpoint for generating quizzes based on given topic
- **[GET] /students/review**: an endpoint for getting AI-generated review

## How to run
1. Clone this repo
2. Create python virtual environment, activate it and installed required dependencies. For more information, refer to [Task 6.1D](https://github.com/alice-tat/Task6_1D_BackendAPI)
3. Install new dependency:
    ```
    pip install Flask-PyMongo
    ```
4. Setup Mongo Atlas and get the connection URI. For mroe information, refer to [dgdeakin/DTask10_1_MongoDBAtlas](https://github.com/dgdeakin/DTask10_1_MongoDBAtlas)
3. Create `.env` file with following information
    ```
    API_TOKEN=<Your generated token>
    API_URL=https://router.huggingface.co/nebius/v1/chat/completions
    MODEL=google/gemma-2-2b-it
    MONGO_URI=<PATH_TO_YOUR_MONGO_ATLAS>
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