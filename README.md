# Welcome to your Expo app 👋

This is an [Expo](https://expo.dev) project created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

---

## Custom Setup Instructions for LearnEase

### 1. Download the Model File

- Download `model.safetensors` from the following Google Drive link: **[https://drive.google.com/file/d/1OJhltoGAX_YwjfEp78iedr4GBn0-7zf0/view?usp=sharing]**
- Place the file in the following directory:
  ```
  \LearnEase\backend\mcq_t5_finetuned1
  ```

### 2. Update IP Address

Update the IP address to your current machine's IP in the following files:

- `\LearnEase\app\screens\login.tsx`
- `\LearnEase\app\screens\register.tsx`
- `\LearnEase\app\(tabs)\summarizer.tsx`
- `\LearnEase\app\quiz.tsx`

Look for any `http://<IP>:<port>` entries and replace `<IP>` with your machine’s current IP address (you can get this using `ipconfig` or `ifconfig`).

### 3. Install Python Dependencies

In the project root or backend directory, install all backend requirements using:

```bash
pip install -r requirements.txt
```

### 4. Run the Project
## Get started (Original Expo Setup)

1. Install dependencies (In thr root directory as well as backend folder)

   ```bash
   npm install
   ```

To run LearnEase properly, open **three separate terminal windows** and execute the following commands:

#### Terminal 1 (Frontend (run this in the root directory))

```bash
npx expo start --clear
```

#### Terminal 2 (Backend Server)

```bash
cd backend
node server.js
```

#### Terminal 3 (FastAPI)(Run this in the root directory)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---


In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

---

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

---

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

---

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.
