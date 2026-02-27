# Deployment Guide

This guide provides step-by-step instructions to deploy the Sentiment Analysis Chatbot application. We will use **MongoDB Atlas** for the database, **Render** for the backend, and **Vercel** for the frontend.

## Prerequisites

*   A GitHub account with this repository pushed to it.
*   Accounts on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas), [Render](https://render.com/), and [Vercel](https://vercel.com/).

---

## Step 1: Database Setup (MongoDB Atlas)

1.  **Create a Cluster:**
    *   Log in to MongoDB Atlas.
    *   Create a new project and click **Build a Database**.
    *   Select the **M0 (Free)** tier.
    *   Choose a provider and region (e.g., AWS / N. Virginia) and click **Create**.

2.  **Configure Security:**
    *   **Database Access:** Go to "Database Access" on the left sidebar. Create a new database user (e.g., `admin`). **Write down the password**.
    *   **Network Access:** Go to "Network Access". Click "Add IP Address" and select **Allow Access from Anywhere** (`0.0.0.0/0`). This allows Render to connect to your database.

3.  **Get Connection String:**
    *   Go back to "Database" and click **Connect** on your cluster.
    *   Select **Drivers** (Python).
    *   Copy the connection string. It will look like:
        `mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority`
    *   **CRITICAL STEP:** You must add the database name to this string. Insert it between the `/` and the `?`.
        *   Incorrect: `...mongodb.net/?...`
        *   Correct: `...mongodb.net/sentiment_db?`
    *   Replace `<password>` with the password you created in the previous step. **Save this string for Step 2.**

---

## Step 2: Backend Deployment (Render)

1.  **Create Web Service:**
    *   Log in to the [Render Dashboard](https://dashboard.render.com/).
    *   Click **New +** and select **Web Service**.
    *   Connect your GitHub repository.

2.  **Configure Service:**
    *   **Name:** `sentiment-backend` (or your preferred name).
    *   **Root Directory:** `backend` (Important!).
    *   **Runtime:** `Python 3`.
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn app:app`

3.  **Environment Variables:**
    *   Scroll down to the "Advanced" section and click "Add Environment Variable". Add the following:
        *   `MONGO_URI`: Paste the connection string from Step 1.
        *   `JWT_SECRET_KEY`: Enter a strong, random secret string (e.g., `my-super-secret-key-123`).
        *   `PYTHON_VERSION`: `3.10.0` (Optional, ensures stability).

4.  **Deploy:**
    *   Click **Create Web Service**.
    *   Wait for the deployment to finish.
    *   Copy the **Service URL** from the top left (e.g., `https://sentiment-backend.onrender.com`). **Save this for Step 3.**

---

## Step 3: Frontend Deployment (Vercel)

1.  **Create Project:**
    *   Log in to the [Vercel Dashboard](https://vercel.com/dashboard).
    *   Click **Add New...** -> **Project**.
    *   Import your GitHub repository.

2.  **Configure Project:**
    *   **Framework Preset:** `Create React App` (should be auto-detected).
    *   **Root Directory:** Click "Edit" next to Root Directory and select `frontend`.

3.  **Environment Variables:**
    *   Expand the "Environment Variables" section.
    *   Add the following variable:
        *   **Name:** `REACT_APP_API_URL`
        *   **Value:** Paste the **Render Backend URL** from Step 2 (e.g., `https://sentiment-backend.onrender.com`). **Do NOT add a trailing slash.**

4.  **Deploy:**
    *   Click **Deploy**.
    *   Once finished, Vercel will provide a domain for your frontend (e.g., `https://sentiment-frontend.vercel.app`).

---

## Verification

1.  Open your **Vercel Frontend URL**.
2.  Try to **Register** a new user. If successful, your database connection is working.
3.  **Login** with the new user. If successful, your backend and JWT handling are working.
4.  Send a message in the chat. If you get a sentiment analysis response, everything is connected correctly!
