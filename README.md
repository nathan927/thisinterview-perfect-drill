# ThisInterview: Perfect Drill

## Project Overview
A modern interview practice platform designed to help users prepare for interviews through question practice, voice recording, and model answer management.

## Key Features
1. **Question Management**
   - Input questions manually or import from text files
   - Export questions for backup or sharing
   - Support for both English and Traditional Chinese

2. **Voice Recording**
   - Record answers for each question
   - Built-in audio playback
   - Save recordings with practice sessions

3. **Model Answers**
   - Add and edit model answers for each question
   - Toggle visibility for self-review
   - Multilingual support

4. **Progress Management**
   - Save complete practice sessions (questions, recordings, model answers)
   - Load previous sessions for review
   - Seamless progress tracking

## Tech Stack
- React 18.2.0
- Material-UI (MUI)
- Styled Components
- Web Audio API

## Setup Instructions
1. Clone the repository
```bash
git clone [repository-url]
cd perfect-drill
```

2. Install dependencies
```bash
npm install
```

3. Start development server
```bash
npm start
```

The application will be available at `http://localhost:3000`

## Usage
1. **Adding Questions**
   - Click "Input Questions" to manually enter questions
   - Use "Import Questions" to load questions from a text file
   - Questions from both methods will be combined

2. **Recording Answers**
   - Navigate to a question
   - Click "Start Recording" to begin
   - Click "Stop Recording" when finished
   - Use the audio player to review your answer

3. **Managing Model Answers**
   - Click "Model Answer" to show/hide the answer field
   - Enter or edit the model answer
   - Answers are saved automatically with your session

4. **Saving Progress**
   - Click "Save Progress" to download your session file
   - Use "Load Progress" to restore a previous session
   - All questions, recordings, and model answers will be preserved

## License
This project is licensed under the MIT License.
