// Questions for team evaluation
const evaluationQuestions = [
    {
      id: 1,
      text: "¿Cual es tu promedio ponderado? Recuerda que esta información no va a ser divulgada con nadie y todos los datos estarán anonimizados",
      type: "text",
      placeholder: "Ingresa tu promedio (ej: 4.25)",
      required: true,
      numeric: true,
      min: 0,
      max: 5,
    },
    {
      id: 2,
      text: "El compañero(a) cumple puntualmente con las tareas asignadas y plazos establecidos",
      type: "matrix",
      required: true,
    },
    {
      id: 3,
      text: "Muestra un alto nivel de dedicación en las actividades del equipo",
      type: "matrix",
      required: true,
    },
    {
      id: 4,
      text: "Comparte información importante de forma clara y oportuna con el equipo",
      type: "matrix",
      required: true,
    },
    {
      id: 5,
      text: "Escucha activamente y valora las ideas u opiniones de los demás miembros",
      type: "matrix",
      required: true,
    },
    {
      id: 6,
      text: "El compañero(a) muestra entusiasmo y disposición para superar los retos del proyecto",
      type: "matrix",
      required: true,
    },
    {
      id: 7,
      text: "Mantiene una actitud positiva incluso cuando surgen dificultades o cambios",
      type: "matrix",
      required: true,
    },
    {
      id: 8,
      text: "El compañero establece objetivos o metas claras dentro del equipo para cada fase/tarea de la actividad",
      type: "matrix",
      required: true,
    },
    {
      id: 9,
      text: "El compañero participa en el seguimiento periódico de las metas y se reorientan cuando es necesario",
      type: "matrix",
      required: true,
    },
    {
      id: 10,
      text: " El compañero valora  y se aprovecha en este equipo las diferencias (habilidades, experiencias) de los otros miembros del equipo",
      type: "matrix",
      required: true,
    },
    {
      id: 11,
      text: "El compañero(a) fomenta espacios donde cada integrante puede aportar su perspectiva sin sentirse excluido(a)",
      type: "matrix",
      required: true,
    },
    {
      id: 12,
      text: "El compañero(a) maneja adecuadamente sus emociones ante el estrés o desacuerdos",
      type: "matrix",
      required: true,
    },
    {
      id: 13,
      text: "Se muestra empático(a) y comprensivo(a) cuando otro miembro enfrenta dificultades",
      type: "matrix",
      required: true,
    },
    {
      id: 14,
      text: "El compañero(a) toma la iniciativa para organizar su trabajo sin necesidad de supervisión constante",
      type: "matrix",
      required: true,
    },
    {
      id: 15,
      text: "Muestra capacidad para tomar decisiones de manera independiente dentro del equipo",
      type: "matrix",
      required: true,
    },
    {
      id: 16,
      text: "El compañero(a) confía en las habilidades y compromiso de los demás miembros del equipo",
      type: "matrix",
      required: true,
    },
    {
      id: 17,
      text: "Es percibido(a) como una persona confiable por sus compañeros de equipo",
      type: "matrix",
      required: true,
    },
    {
      id: 18,
      text: "El compañero(a) expresa satisfacción con el ambiente de trabajo y las dinámicas del equipo",
      type: "matrix",
      required: true,
    },
    {
      id: 19,
      text: "Se siente motivado(a) y comprometido(a) con las tareas asignadas y los objetivos del equipo",
      type: "matrix",
      required: true,
    },
  ];
  
  // DOM elements
  const questionsContainer = document.getElementById("questionsContainer");
  const prevButton = document.getElementById("prevButton");
  const nextButton = document.getElementById("nextButton");
  const pageIndicator = document.getElementById("pageIndicator");
  const progressBar = document.getElementById("progressBar");
  const progressPercentage = document.getElementById("progressPercentage");
  const alertElement = document.getElementById("alert");
  const alertMessage = document.getElementById("alertMessage");
  const introSection = document.getElementById("intro-section");
  
  // State variables
  let currentPage = 1;
  let answers = {};
  let activeQuestionId = 1;
  let questionRefs = [];
  
  // Constants
  const questionsPerPage = 10;
  const totalPages = Math.ceil(evaluationQuestions.length / questionsPerPage);
  
  // Initialize the form
  function initForm() {
    // Try to load saved answers from localStorage
    const savedAnswers = localStorage.getItem("teamCrossEvaluationAnswers");
    if (savedAnswers) {
      try {
        answers = JSON.parse(savedAnswers);
      } catch (e) {
        console.error("Error parsing saved answers:", e);
      }
    }
  
    renderCurrentPage();
    updateProgressBar();
    updatePageIndicator();
    updateButtonStates();
  
    // Set up event listeners
    prevButton.addEventListener("click", goToPrevPage);
    nextButton.addEventListener("click", handleNextButtonClick);
  }
  
  // Render the current page of questions
  function renderCurrentPage() {
    questionsContainer.innerHTML = "";
    questionRefs = [];
  
    // Show intro section only on first page
    if (introSection) {
      introSection.style.display = currentPage === 1 ? "block" : "none";
    }
  
    const startIndex = (currentPage - 1) * questionsPerPage;
    const endIndex = Math.min(startIndex + questionsPerPage, evaluationQuestions.length);
  
    // Add section title for team evaluation if needed
    if (currentPage === 1) {
      const sectionTitle = document.createElement("h3");
      sectionTitle.className = "section-title";
      sectionTitle.textContent = "Información Personal";
      questionsContainer.appendChild(sectionTitle);
    } else if (currentPage === 2 && startIndex <= 19) {
      const sectionTitle = document.createElement("h3");
      sectionTitle.className = "section-title";
      sectionTitle.textContent = "Evaluación de Compañeros de Equipo";
  
      const sectionDescription = document.createElement("p");
      sectionDescription.className = "section-description";
      sectionDescription.textContent =
        "Para cada uno de los integrantes del equipo, califique de 1 (bajo nivel de desempeño) a 5 (alto nivel de desempeño) en la casilla correspondiente, (el evaluador también realiza su autoevaluación), cada una de las conductas utilizando la escala indicada a la derecha de cada nombre.";
  
      questionsContainer.appendChild(sectionTitle);
      questionsContainer.appendChild(sectionDescription);
    } else if (startIndex >= 19) {
      const sectionTitle = document.createElement("h3");
      sectionTitle.className = "section-title";
      sectionTitle.textContent = "Evaluación del Desempeño del Equipo";
  
      const sectionDescription = document.createElement("p");
      sectionDescription.className = "section-description";
      sectionDescription.textContent = "Evalúa el desempeño general del equipo durante este periodo.";
  
      questionsContainer.appendChild(sectionTitle);
      questionsContainer.appendChild(sectionDescription);
    }
  
    for (let i = startIndex; i < endIndex; i++) {
      const question = evaluationQuestions[i];
      const questionElement = createQuestionElement(question);
      questionsContainer.appendChild(questionElement);
      questionRefs.push(questionElement);
    }
  
    // Highlight the active question
    highlightActiveQuestion();
  }
  
  // Create a question element based on its type
// Reemplazo completo de la función createQuestionElement para las preguntas tipo matriz
function createQuestionElement(question) {
  const questionDiv = document.createElement("div");
  questionDiv.className = `question ${answers[question.id] ? "completed" : ""} ${activeQuestionId === question.id ? "active" : ""}`;
  questionDiv.dataset.id = question.id;

  // Question header with number and text
  const questionHeader = document.createElement("div");
  questionHeader.className = "question-header";

  const questionNumber = document.createElement("div");
  questionNumber.className = "question-number";
  questionNumber.textContent = question.id;

  const questionText = document.createElement("div");
  questionText.className = "question-text";
  questionText.textContent = question.text;

  if (question.required) {
    const requiredSpan = document.createElement("span");
    requiredSpan.className = "required";
    requiredSpan.textContent = " *";
    questionText.appendChild(requiredSpan);
  }

  questionHeader.appendChild(questionNumber);
  questionHeader.appendChild(questionText);
  questionDiv.appendChild(questionHeader);

  // Question content based on type
  const questionContent = document.createElement("div");
  questionContent.className = "question-content";

  if (question.type === "text") {
    // Código para preguntas de texto (sin cambios)
    const input = document.createElement("input");
    input.type = question.numeric ? "number" : "text";
    input.className = "input-field";
    input.placeholder = question.placeholder || "";
    input.value = answers[question.id] || "";
    if (question.min !== undefined) input.min = question.min;
    if (question.max !== undefined) input.max = question.max;

    input.addEventListener("input", (e) => handleAnswerChange(question.id, e.target.value));

    questionContent.appendChild(input);

    if (question.helperText) {
      const helperText = document.createElement("div");
      helperText.className = "helper-text";
      helperText.textContent = question.helperText;
      questionContent.appendChild(helperText);
    }
  } else if (question.type === "matrix") {
    // Create a table for team member evaluation
    const table = document.createElement("table");
    table.className = "team-matrix";

    // Create header row
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    // Empty cell for member names
    const emptyHeader = document.createElement("th");
    headerRow.appendChild(emptyHeader);

    // Rating headers (1-5)
    for (let i = 1; i <= 5; i++) {
      const ratingHeader = document.createElement("th");
      ratingHeader.textContent = i;
      headerRow.appendChild(ratingHeader);
    }

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create body with team members
    const tbody = document.createElement("tbody");

    teamMembers.forEach((member) => {
      const memberRow = document.createElement("tr");

      // Member name cell
      const nameCell = document.createElement("td");
      nameCell.className = "member-name";
      nameCell.textContent = member.name;
      memberRow.appendChild(nameCell);

      // Rating cells (1-5)
      for (let rating = 1; rating <= 5; rating++) {
        const ratingCell = document.createElement("td");

        const radioInput = document.createElement("input");
        radioInput.type = "radio";
        // Nombre único para cada combinación de pregunta y miembro
        radioInput.name = `question-${question.id}-member-${member.id}`;
        radioInput.value = rating;
        radioInput.id = `question-${question.id}-member-${member.id}-rating-${rating}`;
        radioInput.className = "rating-radio";

        // Check if this rating is selected for this member
        const memberAnswers = answers[question.id] || {};
        if (memberAnswers[member.id] === rating.toString()) {
          radioInput.checked = true;
        }

        radioInput.addEventListener("change", () => {
          if (radioInput.checked) {
            handleMatrixAnswerChange(question.id, member.id, rating.toString());
          }
        });

        ratingCell.appendChild(radioInput);
        memberRow.appendChild(ratingCell);
      }

      tbody.appendChild(memberRow);
    });

    table.appendChild(tbody);
    questionContent.appendChild(table);
  } else if (question.type === "rating") {
    // Código para preguntas de rating (sin cambios)
    if (question.scaleDescription && question.scaleDescription.length > 0) {
      const scaleDiv = document.createElement("div");
      scaleDiv.className = "scale-description";

      const scaleTitle = document.createElement("h4");
      scaleTitle.textContent = "Escala:";
      scaleDiv.appendChild(scaleTitle);

      const scaleList = document.createElement("ul");
      question.scaleDescription.forEach((desc) => {
        const listItem = document.createElement("li");
        listItem.textContent = desc;
        scaleList.appendChild(listItem);
      });

      scaleDiv.appendChild(scaleList);
      questionContent.appendChild(scaleDiv);
    }

    // Create rating options
    const radioGroup = document.createElement("div");
    radioGroup.className = "radio-group";

    for (let rating = 1; rating <= 5; rating++) {
      const radioOption = document.createElement("div");
      radioOption.className = "radio-option";

      const radioInput = document.createElement("input");
      radioInput.type = "radio";
      radioInput.name = `question-${question.id}`;
      radioInput.value = rating;
      radioInput.id = `question-${question.id}-${rating}`;
      radioInput.checked = answers[question.id] === rating.toString();

      radioInput.addEventListener("change", () => {
        if (radioInput.checked) {
          handleAnswerChange(question.id, rating.toString());
        }
      });

      const radioLabel = document.createElement("label");
      radioLabel.className = "radio-label";
      radioLabel.htmlFor = `question-${question.id}-${rating}`;
      radioLabel.textContent = rating;

      radioOption.appendChild(radioInput);
      radioOption.appendChild(radioLabel);
      radioGroup.appendChild(radioOption);
    }

    questionContent.appendChild(radioGroup);
  }

  questionDiv.appendChild(questionContent);
  return questionDiv;
}
  
  // Handle answer change for regular questions
 function handleAnswerChange(questionId, value) {
  const question = evaluationQuestions.find((q) => q.id === questionId);
  if (!question) return;

  // Validate the answer
  if (!validateAnswer2(question, value)) {
    return;
  }

  // Clear any previous errors
  hideAlert();

  // Update the answer
  answers[questionId] = value;
  localStorage.setItem("teamCrossEvaluationAnswers", JSON.stringify(answers));

  // Mark the question as completed
  const questionElement = document.querySelector(`.question[data-id="${questionId}"]`);
  if (questionElement) {
    questionElement.classList.add("completed");
    questionElement.classList.remove("incomplete");  // ✅ Elimina borde rojo si fue respondida
  }

  // Update progress
  updateProgressBar();

  // Find next unanswered question on current page
  const currentPageQuestions = getCurrentPageQuestions();
  const currentIndex = currentPageQuestions.findIndex((q) => q.id === questionId);

  if (currentIndex < currentPageQuestions.length - 1) {
    // Move to next question on this page
    const nextQuestion = currentPageQuestions[currentIndex + 1];
    setActiveQuestion(nextQuestion.id);
  }

  // Update button states
  updateButtonStates();
}

  
  // Handle answer change for matrix questions
  function handleMatrixAnswerChange(questionId, memberId, value) {
    // Clear any previous errors
    hideAlert();
  
    // Verificar que el memberId no sea undefined o null
    if (!memberId) {
      console.error("Error: memberId es undefined o null");
      return;
    }
  
    // Initialize the question's answers if not already done
    if (!answers[questionId]) {
      answers[questionId] = {};
    }
  
    // Update the answer for this member
    answers[questionId][memberId] = value;
    localStorage.setItem("teamCrossEvaluationAnswers", JSON.stringify(answers));
  
    // Check if all members have been rated for this question
    const allMembersRated = teamMembers.every((member) => {
      // Verificar que el member.id exista antes de usarlo
      return member && member.id && answers[questionId] && answers[questionId][member.id];
    });
  
    // Mark the question as completed if all members are rated
    const questionElement = document.querySelector(`.question[data-id="${questionId}"]`);
    if (questionElement && allMembersRated) {
      questionElement.classList.add("completed");
    }
  
    // Update progress
    updateProgressBar();
  
    // If all members are rated, move to the next question
    if (allMembersRated) {
      const currentPageQuestions = getCurrentPageQuestions();
      const currentIndex = currentPageQuestions.findIndex((q) => q.id === questionId);
  
      if (currentIndex < currentPageQuestions.length - 1) {
        // Move to next question on this page
        const nextQuestion = currentPageQuestions[currentIndex + 1];
        setActiveQuestion(nextQuestion.id);
      }
    }
  
    // Update button states
    updateButtonStates();
  }
  
  // Validate answer based on question type
 function validateAnswer2(question, value) {
    if (value === "") return false;

    if (question.type === "text" && question.numeric) {
      value = value.trim().replace(",", ".");  // 🔧 Normaliza a punto decimal

      // Check format: sólo dígitos, punto opcional, hasta 2 decimales
      if (!/^\d+(\.\d{1,2})?$/.test(value)) {
        showAlert(`La pregunta ${question.id} requiere un número válido (usa máximo 2 decimales, ej: 4.25).`);
        return false;
      }

      const numValue = Number.parseFloat(value);
      if (question.min !== undefined && numValue < question.min) {
        showAlert(`El valor del promedio debe ser mayor o igual a ${question.min}.`);
        return false;
      }
      if (question.max !== undefined && numValue > question.max) {
        showAlert(`El valor del promedio debe ser menor o igual a ${question.max}.`);
        return false;
      }
    }

    return true;
  }

  
  // Get current page questions
  function getCurrentPageQuestions() {
    const startIndex = (currentPage - 1) * questionsPerPage;
    return evaluationQuestions.slice(startIndex, Math.min(startIndex + questionsPerPage, evaluationQuestions.length));
  }
  
  // Set active question
  function setActiveQuestion(questionId) {
    activeQuestionId = questionId;
    highlightActiveQuestion();
  
    // Scroll to the active question
    const activeQuestion = document.querySelector(`.question[data-id="${questionId}"]`);
    if (activeQuestion) {
      activeQuestion.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }
  
  // Highlight the active question
  function highlightActiveQuestion() {
    document.querySelectorAll(".question").forEach((q) => {
      q.classList.remove("active");
    });
  
    const activeQuestion = document.querySelector(`.question[data-id="${activeQuestionId}"]`);
    if (activeQuestion) {
      activeQuestion.classList.add("active");
    }
  }
  
  // Update progress bar
  function updateProgressBar() {
    let completedCount = 0;
    let totalCount = 0;
  
    // Count completed questions
    evaluationQuestions.forEach((question) => {
      if (question.type === "matrix") {
        // For matrix questions, check if all team members are rated
        const allMembersRated = teamMembers.every((member) => {
          return member && member.id && answers[question.id] && answers[question.id][member.id];
        });
        if (allMembersRated) completedCount++;
      } else {
        // For regular questions
        if (answers[question.id]) completedCount++;
      }
      totalCount++;
    });
  
    const percent = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;
  
    progressBar.style.width = `${percent}%`;
    progressPercentage.textContent = `${Math.round(percent)}%`;
  }
  
  // Update page indicator
  function updatePageIndicator() {
    pageIndicator.textContent = `Página ${currentPage} de ${totalPages}`;
  }
  
  // Check if current page is complete
  function isCurrentPageComplete() {
    const currentPageQuestions = getCurrentPageQuestions();
    return currentPageQuestions.every((question) => {
      if (question.type === "matrix") {
        // For matrix questions, check if all team members are rated
        return teamMembers.every((member) => answers[question.id] && answers[question.id][member.id]);
      } else {
        // For regular questions
        return answers[question.id] !== undefined && answers[question.id] !== "";
      }
    });
  }
  
  // Check if all questions are answered
  function isFormComplete() {
    return evaluationQuestions.every((question) => {
      if (question.type === "matrix") {
        // For matrix questions, check if all team members are rated
        return teamMembers.every((member) => {
          return member && member.id && answers[question.id] && answers[question.id][member.id];
        });
      } else {
        // For regular questions
        return answers[question.id] !== undefined && answers[question.id] !== "";
      }
    });
  }
  
  // Update button states
  function updateButtonStates() {
    prevButton.disabled = currentPage === 1;
  
    if (currentPage < totalPages) {
      nextButton.textContent = "Siguiente";
      nextButton.className = "btn primary";
      
    } else {
      nextButton.textContent = "Finalizar";
      nextButton.className = "btn success";
      
    }
  }
  
  // Go to previous page
  function goToPrevPage() {
    if (currentPage > 1) {
      currentPage--;
      renderCurrentPage();
      updatePageIndicator();
      updateButtonStates();
  
      // Set active question to first question on the page
      const firstQuestion = getCurrentPageQuestions()[0];
      if (firstQuestion) {
        setActiveQuestion(firstQuestion.id);
      }
  
      window.scrollTo(0, 0);
    }
  }
  
  // Handle next button click
function handleNextButtonClick() {
  if (currentPage < totalPages) {
    if (!isCurrentPageComplete()) {
      const currentPageQuestions = getCurrentPageQuestions();
      const firstIncomplete = currentPageQuestions.find((q) => {
        if (q.type === "matrix") {
          return !teamMembers.every((m) => answers[q.id] && answers[q.id][m.id]);
        } else {
          return !answers[q.id];
        }
      });

      if (firstIncomplete) {
        const questionElement = document.querySelector(`.question[data-id="${firstIncomplete.id}"]`);
        if (questionElement) {
          questionElement.classList.add("incomplete");
          questionElement.scrollIntoView({ behavior: "smooth", block: "center" });
        }
        showAlert(`⚠ Por favor responde la pregunta ${firstIncomplete.id} antes de continuar.`);
        return;
      }
    }

    goToNextPage();
  } else {
    submitForm();
  }
}


  
  // Go to next page
  function goToNextPage() {
    if (currentPage < totalPages) {
      currentPage++;
      renderCurrentPage();
      updatePageIndicator();
      updateButtonStates();
  
      // Set active question to first question on the page
      const firstQuestion = getCurrentPageQuestions()[0];
      if (firstQuestion) {
        setActiveQuestion(firstQuestion.id);
      }
  
      window.scrollTo(0, 0);
    }
  }
  
  // Submit the form
  function submitForm() {
    for (const question of evaluationQuestions) {
      const questionElement = document.querySelector(`.question[data-id="${question.id}"]`);

      if (question.type === "matrix") {
        const allRated = teamMembers.every((member) => {
          return member && member.id && answers[question.id] && answers[question.id][member.id];
        });

        if (!allRated) {
          if (questionElement) {
            questionElement.classList.add("incomplete");
            questionElement.scrollIntoView({ behavior: "smooth", block: "center" });
          }
          showAlert(`⚠ Por favor completa todas las evaluaciones para la pregunta ${question.id}.`);
          return;
        }

        // Limpiar respuestas inválidas
        if (answers[question.id] && answers[question.id]["undefined"]) {
          delete answers[question.id]["undefined"];
        }

      } else {
        const answer = answers[question.id];

        if (answer === undefined || answer === "") {
          if (questionElement) {
            questionElement.classList.add("incomplete");
            questionElement.scrollIntoView({ behavior: "smooth", block: "center" });
          }
          showAlert(`⚠ Por favor responde la pregunta ${question.id}.`);
          return;
        }

        if (question.type === "text" && question.numeric && !validateAnswer2(question, answer)) {
          if (questionElement) {
            questionElement.classList.add("incomplete");
            questionElement.scrollIntoView({ behavior: "smooth", block: "center" });
          }
          return;
        }
      }
  }

  // Si pasa todas las validaciones, enviar
  fetch(`/student/submit-coevaluation/${classId}/${activityId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(answers),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showNotification(data.message);
        localStorage.removeItem("teamCrossEvaluationAnswers");
        setTimeout(() => {
          window.location.href = `/student/clases/${classId}`;
        }, 1500);
      } else {
        showAlert(data.message || "Error al enviar el formulario");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showAlert("Error al enviar el formulario. Por favor intente nuevamente.");
    });
}

  
  // Show notification message
  function showNotification(message) {
    // Create notification element
    const notification = document.createElement("div");
    notification.className = "notification success";
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">✓</span>
            <span class="notification-message">${message}</span>
        </div>
    `;
  
    // Add to document
    document.body.appendChild(notification);
  
    // Remove after 3 seconds
    setTimeout(() => {
      notification.classList.add("fade-out");
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }
  
  // Show alert message
 function showAlert(message) {
  alertMessage.textContent = message;
  alertElement.classList.remove("hidden");

  const alertSound = document.getElementById("alertSound");
  if (alertSound) {
    alertSound.currentTime = 0; // reinicia si ya se estaba reproduciendo
    alertSound.play().catch(e => console.warn("Audio not played:", e));
  }
}
  
  // Hide alert message
  function hideAlert() {
    alertElement.classList.add("hidden");
  }
  
  // Make closeAlert function available globally
  window.closeAlert = hideAlert;
  
  // Initialize the form when the DOM is loaded
  document.addEventListener("DOMContentLoaded", initForm);