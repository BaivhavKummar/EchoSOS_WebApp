# EchoSOS_WebApp
Interactive prototype for the EchoSOS acoustic rescue beacon project

---

# EchoSOS: A Dual-Use Emergency Communication Platform

## The Problem: When Communication Fails, Lives are at Risk

In any crisis, communication is the key to safety. However, the methods we rely on are fragile and often fail us in two critical, yet opposite, scenarios:

1.  **The Disconnected Crisis (Wilderness & Disasters):** Following a natural disaster or in remote, off-grid locations, infrastructure fails. There is no cell service and no Wi-Fi. A person trapped, injured, or lost has no way to send a signal for help. GPS can tell them where they are, but it can't tell anyone else, creating a deadly communication void.
2.  **The Connected Crisis (Urban Threats):** In a city, making a 911 call during an emergency like a public harassment incident, assault, or robbery is often too slow and dangerously public. The act of calling can escalate the threat. A silent, instant, and data-rich method of alerting authorities is desperately needed.

The world lacks a single, versatile platform that can intelligently adapt to provide the right communication tool for the right crisis.

## Our Solution: EchoSOS - A Two-Mode Safety Ecosystem

EchoSOS is a dual-use emergency platform engineered to solve both the disconnected and connected crises. It provides the right tool for the right situation through two specialized modes.

### 1. EchoSOS Rescue: The Offline Lifeline

For disconnected scenarios where there is no network, EchoSOS transforms a smartphone into a multi-layered rescue beacon that operates **completely offline**.

*   **Technology Stack:** React Native/Flutter, Native Modules (Swift/Kotlin), GPS, Bluetooth LE APIs, Real-time Audio Processing (FFT).
*   **How it Works (Cascading Signal System):**
    *   **Layer 1 (Long-Range Discovery > 1km): The Bluetooth Mesh Network.** Our most powerful feature. An SOS beacon is automatically "hopped" from one rescuer's device to the next, creating a self-healing ad-hoc network that relays a distress signal for kilometers.
    *   **Layer 2 (Mid-Range Navigation ~200m): The Bluetooth + Offline GPS Beacon.** The app broadcasts the user's precise, offline GPS coordinates via a Bluetooth 5.0 (BLE) signal. Rescuers can detect this from hundreds of meters away and navigate directly to the location.
    *   **Layer 3 (Close-Range Pinpointing < 30m): The Acoustic Beacon.** For the final stage of a rescue, the app emits an optimized acoustic chirp (3-8 kHz) that can penetrate obstacles like rubble or snow, allowing rescuers to pinpoint the victim's exact physical location.

### 2. EchoSOS City: The Urban Guardian

For connected urban environments, EchoSOS leverages cloud computing and the phone's data connection to provide a silent, instant, and intelligent alert system.

*   **Technology Stack:** React Native/Flutter, AWS Serverless Backend (API Gateway, Lambda, DynamoDB, Cognito, SNS), React/Vue Web Dashboard.
*   **How it Works (Cloud-Powered Dispatch):**
    1.  **Silent Alert:** A user in distress discreetly presses a pre-defined alert button on the app (e.g., "Public Harassment," "Medical Emergency").
    2.  **Instant Data Transmission:** The app immediately sends a secure data packet containing the alert type and live GPS location to the **EchoSOS Cloud Platform**.
    3.  **Cloud Processing & Dispatch:** The cloud backend authenticates the user, processes the alert, and instantly pushes the data-rich incident report to two places:
        *   A secure **First Responder Web Dashboard** for dispatch command centers.
        *   A silent **push notification** to the mobile devices of nearby, on-duty police and medical teams.
*   **The Outcome:** A response that is faster, more discreet, and better informed than a traditional 911 call.

## Features at a Glance

| Feature | Mode | Description |
| :--- | :--- | :--- |
| **Bluetooth Mesh Network** | Rescue | Enables long-range (>1km) offline signal relaying between devices. |
| **Offline GPS-to-BLE Beacon** | Rescue | Broadcasts precise GPS coordinates over Bluetooth for direct navigation. |
| **Acoustic Pinpoint Beacon** | Rescue | Uses an optimized audio chirp for final, close-range location through obstacles. |
| **Silent Contextual Alerts**| City | Allows users to instantly report the *type* of emergency without speaking. |
| **Cloud Dispatch Dashboard**| City | A live, web-based map for first responders to view and manage incoming alerts. |

## Methodology and Implementation

Our project is architected with a clear separation of concerns:

-   **Mobile Application (Cross-Platform):** A single app built with React Native or Flutter provides the user interface for both modes.
-   **Offline Engine (Native Modules):** Low-level hardware interactions for GPS, Bluetooth, and audio are handled by native code for maximum performance and reliability. The signal processing logic for the acoustic beacon is prototyped in Python and implemented natively.
-   **Online Backend (AWS Serverless):** The City mode is powered by a fully serverless backend on AWS. This ensures massive scalability, high availability, and low operational cost, making it ideal for a public safety application.

## Future Scope & Commercialization

We envision a two-track roadmap for EchoSOS:

1.  **RESCUE (Free for Public Good):** We will continue to enhance the offline features, fully implementing the Bluetooth Mesh protocol. The Rescue mode will **always be free** for individuals and official Search & Rescue organizations.
2.  **CITY (B2B/B2G SaaS Model):** We will build out the full cloud platform and partner with municipalities, university campuses, and private security firms to license the **EchoSOS City** system. This B2B/B2G revenue model will ensure the project's long-term sustainability and fund the continued development of the free Rescue app.

---
