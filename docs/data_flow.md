# Data Flow Diagram

This diagram visualises how data moves through the application, from user authentication to referral submission and dashboard access.

```mermaid
graph TD
    %% User Roles
    Referrer((Referrer/Professional))
    Referee((Family/Referee))

    %% Authentication Flow
    subgraph Auth [Authentication]
        Reg[Register /login.html]
        Log[Login /login.html]
    end

    %% Data Stores
    subgraph Storage [In-Memory Store]
        RefStore[(Referrers Store)]
        RefereeStore[(Referees Store)]
    end

    %% Form Flow
    subgraph ReferralForm [Multi-Step Referral Form]
        Step1[Child Details]
        Step2[Address]
        Step3[Parent Details]
        Step4[Referrer Details]
        Step5[Service Type/Selection]
        Step6[Additional Info]
        Step7[Consent]
        Check[Check Answers]
    end

    %% Referrer Path
    Referrer --> Reg & Log
    Reg & Log <--> RefStore
    Log -->|Success| Start[Start Referral]
    Start --> Step1
    Step1 --> Step2 --> Step3 --> Step4 --> Step5 --> Step6 --> Step7 --> Check
    
    %% Session Storage during form
    ReferralForm -.->|Data held in| Session[(Flask Session)]

    %% Submission
    Check -->|Submit POST| Process{Process Referral}
    Process -->|Generate Ref #| RefereeStore
    Process -->|Link Ref to| RefStore
    Process -->|Redirect| Conf[Confirmation]

    %% Dashboard Access
    Referrer -->|View Submissions| DashR[Referrer Dashboard]
    DashR <--> RefStore
    DashR --- RefereeStore

    Referee -->|Login with Ref # + Postcode| DashF[Referee Dashboard]
    DashF <--> RefereeStore
```

## Key Components

### 1. Flask Session
During the referral process, data is temporarily stored in the `session["answers"]` dictionary. This prevents data loss as the user moves between steps and allows for the "Back" button functionality.

### 2. In-Memory Store (`app/store.py`)
- **Referrers:** Stores user credentials (hashed) and a list of reference numbers they have submitted.
- **Referees:** Stores the full details of a submitted referral, keyed by a unique 8-character reference code.

### 3. Data Persistence
Upon clicking "Accept and send" on the **Check** page:
1. A unique reference ID is generated.
2. The data is moved from the **Session** to the **Referees Store**.
3. The reference ID is appended to the **Referrer's** list of submissions.
4. The session is cleared of the temporary answers.
