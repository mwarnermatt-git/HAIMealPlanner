# HAIMealPlanner

This repo contains everything someone should need to replicate my Home Assistant AI Meal Planner. This is not very polished, but it works well. 

Prerequesites:
* [OpenAI API Key](https://platform.openai.com/account/api-keys)
* [YouTube API Key](https://blog.hubspot.com/website/how-to-get-youtube-api-key)
* [Home Assistant instance and Long Lived Access Token](https://developers.home-assistant.io/docs/auth_api/#:~:text=Long%2Dlived%20access%20tokens%20can,access%20token%20for%20current%20user.)
* [PythonScriptsPro add-on](https://github.com/AlexxIT/PythonScriptsPro)

1. Set up your keys.
2. Install PythonScriptsPro.
3. Create entities in configuration.yaml.
4. Create images and fonts directories in you www folder.
5. Copy python scripts to your python_scripts folder.
6. Create your markdown card to display your meal planner entities. 
7. Create scripts to call the pythonscriptspro Home Assistant service. 
8. Run the scripts and verify your entities are updating and images are generating as expected. 

