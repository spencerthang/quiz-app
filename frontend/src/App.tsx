import React, { FunctionComponent, useState, useEffect } from "react";
import "./App.css";
import { Button, FormGroup, InputGroup } from "@blueprintjs/core";

import "normalize.css";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import { time } from "console";

const API_URL = "";
const QUESTION_TIMEOUT = 10;

type QuestionState = {
  question: String;
};

const getQuestions = async (username: string) => {
  const response = await fetch(`${API_URL}/start_quiz?username=${username}`);
  if (response.status !== 200) {
    alert("An error occurred!");
    return;
  }
  const body = await response.json();
  return body;
};

const submitResponse = async (
  username: string,
  questionId: number,
  responseText: string
) => {
  const response = await fetch(
    `${API_URL}/submit_response?username=${username}&question_id=${questionId}&response_text=${responseText}`
  );
  if (response.status !== 200) {
    alert("An error occurred!");
    return false;
  }
  return true;
};

export const Quiz: FunctionComponent<{}> = () => {
  const [username, setUsername] = useState<string>("");
  const [responseText, setResponseText] = useState<string>("");
  const [questions, setQuestions] = useState<any>(null);
  const [currentQuestion, setCurrentQuestion] = useState<number>(0);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  const loadNextQuestion = () => {
    setCurrentQuestion(currentQuestion + 1);
    setResponseText("");
    setTimeRemaining(QUESTION_TIMEOUT);
  }

  useEffect(() => {
    const interval = setInterval(() => {
      if (timeRemaining !== null) {
        if (timeRemaining > 0) {
          setTimeRemaining(timeRemaining - 1);
        } else if (timeRemaining === 0) {
          loadNextQuestion();
        }
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [timeRemaining]);

  if (questions === null) {
    return (
      <form
        onSubmit={(e) => {
          e.preventDefault();
          // Load Quiz
          getQuestions(username).then((response) => {
            setQuestions(response);
            setTimeRemaining(QUESTION_TIMEOUT);
          });
        }}
      >
        <FormGroup>
          <InputGroup
            id="username"
            placeholder="Username"
            value={username}
            onChange={(ev: React.ChangeEvent<HTMLInputElement>) =>
              setUsername(ev.target.value)
            }
          />
          <Button type="submit" text="Load Quiz" />
        </FormGroup>
      </form>
    );
  } else if (currentQuestion < questions.length) {
    return (
      <form
        onSubmit={(e) => {
          setTimeRemaining(null);
          e.preventDefault();
          // Submit Response
          const q = questions[currentQuestion];
          submitResponse(username, q.question_id, responseText).then(
            (success) => {
              if (success) {
                loadNextQuestion();
              }
            }
          );
        }}
      >
        <p>
          Question {currentQuestion + 1} of {questions.length}<br />
          Time left: {timeRemaining == null ? '...' : new Date(timeRemaining * 1000).toISOString().substr(11, 8)}
        </p>
        <FormGroup>
          <p>Q. {questions[currentQuestion].question_text}</p>
          <InputGroup
            id="response"
            placeholder="Response"
            value={responseText}
            onChange={(ev: React.ChangeEvent<HTMLInputElement>) =>
              setResponseText(ev.target.value)
            }
          />
          <Button type="submit" text="Submit" />
        </FormGroup>
      </form>
    );
  } else {
    return <p>Complete</p>;
  }
};

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <div>
          Quiz App
          <Quiz />
        </div>
      </header>
    </div>
  );
}

export default App;
