// Rating questions (1-5 scale)
const ratingQuestions = [//no
    {
      id: 14,
      text: "¿A qué grupo de trabajo perteneces?",
      type: "text",
      placeholder: "Escribe tu respuesta",
      required: true,
    },
    {
      id: 15,
      text: "¿Aprendo cómo obtener los recursos externos que necesita nuestro equipo para tener éxito?",
      type: "rating",
      required: true,
    },
    {
      id: 16,
      text: "¿Me siento cómodo siendo crítico con mis compañeros de equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 17,
      text: "¿Me gusta cuando estamos ocupados y logramos completar tareas?",
      type: "rating",
      required: true,
    },
    {
      id: 18,
      text: "¿Me gusta desafiar las suposiciones de las personas?",
      type: "rating",
      required: true,
    },
    {
      id: 19,
      text: "¿Me gusta ser quien se encarga de los detalles de un proyecto en equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 20,
      text: "¿A menudo ofrezco nuevas ideas y sugerencias sin que me pregunten mi opinión?",
      type: "rating",
      required: true,
    },
    {
      id: 21,
      text: "¿Puedo calmar a las personas y enfocarlas en la tarea cuando las cosas se ponen estresantes?",
      type: "rating",
      required: true,
    },
    {
      id: 22,
      text: "¿Me gusta ser quien decide qué tareas hará cada persona en un equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 23,
      text: "¿Soy quien cuestiona por qué estamos haciendo las cosas de cierta manera?",
      type: "rating",
      required: true,
    },
    {
      id: 24,
      text: "¿A veces simplemente expreso una opinión diferente para mantener a mi equipo pensando sobre lo que debemos hacer?",
      type: "rating",
      required: true,
    },
    {
      id: 25,
      text: "¿Siempre estoy dispuesto a apoyar una buena sugerencia en beneficio del equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 26,
      text: "¿Mis compañeros de equipo suelen recurrir a mí cuando algo necesita ser hecho?",
      type: "rating",
      required: true,
    },
    {
      id: 27,
      text: "¿Me gusta probar nuevas ideas y enfoques?",
      type: "rating",
      required: true,
    },
    {
      id: 28,
      text: "¿Cuestiono lo que mi equipo debe hacer para cumplir con la tarea?",
      type: "rating",
      required: true,
    },
    {
      id: 29,
      text: "¿Puedo ser confiable para seguir adelante con cualquier tarea que me hayan asignado?",
      type: "rating",
      required: true,
    },
    {
      id: 30,
      text: "¿Puedo ser confiable cuando una tarea necesita ser realizada?",
      type: "rating",
      required: true,
    },
    {
      id: 31,
      text: "¿Mantengo a mi equipo al ritmo adecuado y consciente de los plazos?",
      type: "rating",
      required: true,
    },
    {
      id: 32,
      text: "¿Me aseguro de que mis compañeros de equipo tengan claras sus responsabilidades?",
      type: "rating",
      required: true,
    },
    {
      id: 33,
      text: "¿Me siento cómodo manejando conflictos interpersonales y ayudando a las personas a resolverlos?",
      type: "rating",
      required: true,
    },
    {
      id: 34,
      text: "¿Disfruto coordinando los esfuerzos del equipo con personas o grupos fuera del equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 35,
      text: "¿Mi enfoque principal es cumplir con mis tareas para el equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 36,
      text: "¿Puedo ser confiable para difundir ideas entre mi equipo y personas fuera de él?",
      type: "rating",
      required: true,
    },
    {
      id: 37,
      text: "¿Me siento cómodo siendo el portavoz de un equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 38,
      text: "¿Soy quien da un paso adelante y hace lo necesario para que el equipo tenga éxito?",
      type: "rating",
      required: true,
    },
    {
      id: 39,
      text: "¿A menudo soy el primero en ofrecerme para una tarea difícil o impopular si es lo que el equipo necesita?",
      type: "rating",
      required: true,
    },
    {
      id: 40,
      text: "¿Me gusta ser quien lleva el control sobre cómo está haciendo las cosas mi equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 41,
      text: "¿Suelo ser quien sugiere una nueva idea o dirección cuando el equipo se estanca?",
      type: "rating",
      required: true,
    },
    {
      id: 42,
      text: "¿Aporto un sentido de organización a cualquier trabajo que realice un equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 43,
      text: "¿Me aburro cuando hacemos la misma tarea de la misma manera cada vez?",
      type: "rating",
      required: true,
    },
    {
      id: 44,
      text: "¿Estructuro las actividades del equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 45,
      text: "¿Descubro y me conecto con personas que pueden ayudar a que mi equipo tenga éxito?",
      type: "rating",
      required: true,
    },
    {
      id: 46,
      text: "¿No tengo miedo de cuestionar la autoridad de mis compañeros de equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 47,
      text: '¿Soy conocido por pensar de manera creativa y "fuera de la caja"?',
      type: "rating",
      required: true,
    },
    {
      id: 48,
      text: "¿Normalmente me entero de lo que sucede fuera de mi equipo y comparto esa información con mis compañeros?",
      type: "rating",
      required: true,
    },
    {
      id: 49,
      text: "¿Me gusta encontrar nuevas formas en que nuestro equipo puede cumplir con sus tareas?",
      type: "rating",
      required: true,
    },
    {
      id: 50,
      text: "¿Normalmente sugiero los pasos apropiados que mi equipo debe seguir para hacer algo?",
      type: "rating",
      required: true,
    },
    {
      id: 51,
      text: "¿Me gusta ayudar a diferentes tipos de personas a trabajar eficazmente juntas?",
      type: "rating",
      required: true,
    },
    {
      id: 52,
      text: "¿Me siento cómodo produciendo y compartiendo nuevas ideas con mi equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 53,
      text: "¿A menudo trabajo para mantener buenas relaciones laborales dentro de mi equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 54,
      text: "¿Me molesta ver a mis compañeros frustrados o deprimidos?",
      type: "rating",
      required: true,
    },
    {
      id: 55,
      text: "¿Siempre estoy comprometido con las tareas de mi equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 56,
      text: "¿A menudo señalo los riesgos o peligros potenciales de un plan o curso de acción del equipo?",
      type: "rating",
      required: true,
    },
    {
      id: 57,
      text: "¿Ayudo a las personas a superar sus desacuerdos y encontrar un terreno común?",
      type: "rating",
      required: true,
    },
    {
      id: 58,
      text: "¿Mis compañeros de equipo suelen considerar mis sugerencias como creativas o innovadoras?",
      type: "rating",
      required: true,
    },
    {
      id: 59,
      text: "¿A menudo sirvo de enlace entre mi equipo y grupos externos?",
      type: "rating",
      required: true,
    },
    {
      id: 60,
      text: "¿Promuevo la misión y los objetivos de mi equipo con otros equipos o unidades?",
      type: "rating",
      required: true,
    },
    {
      id: 61,
      text: "¿Normalmente puedo proporcionar una justificación sólida para refutar ideas que considero insostenibles?",
      type: "rating",
      required: true,
    },
    {
      id: 62,
      text: "¿Animo a mis compañeros cuando sé que tienen una tarea difícil o un desafío?",
      type: "rating",
      required: true,
    },
  ]
  
  // Rating labels
  const ratingLabels = [
    { value: "1", label: "Totalmente en desacuerdo" },
    { value: "2", label: "En desacuerdo" },
    { value: "3", label: "Neutral" },
    { value: "4", label: "De acuerdo" },
    { value: "5", label: "Totalmente de acuerdo" },
  ]
  
  // DOM elements
  const questionsContainer = document.getElementById("questionsContainer")
  const prevButton = document.getElementById("prevButton")
  const nextButton = document.getElementById("nextButton")
  const pageIndicator = document.getElementById("pageIndicator")
  const progressBar = document.getElementById("progressBar")
  const progressPercentage = document.getElementById("progressPercentage")
  const alertElement = document.getElementById("alert")
  const alertMessage = document.getElementById("alertMessage")
  const introSection = document.getElementById("intro-section")
  
  // State variables
  let currentPage = 1
  let answers = {}
  let activeQuestionId = 14 // Start with the first rating question
  let questionRefs = []
  
  // Constants
  const questionsPerPage = 10
  const totalPages = Math.ceil(ratingQuestions.length / questionsPerPage)
  
  // Initialize the form
  function initForm() {
    // Try to load saved answers from localStorage
    const savedAnswers = localStorage.getItem("teamRoleAnswers")
    if (savedAnswers) {
      try {
        answers = JSON.parse(savedAnswers)
      } catch (e) {
        console.error("Error parsing saved answers:", e)
      }
    }
  
    renderCurrentPage()
    updateProgressBar()
    updatePageIndicator()
    updateButtonStates()
  
    // Set up event listeners
    prevButton.addEventListener("click", goToPrevPage)
    nextButton.addEventListener("click", handleNextButtonClick)
  }
  
  // Render the current page of questions
  function renderCurrentPage() {
    questionsContainer.innerHTML = ""
    questionRefs = []
  
    // Show intro section only on first page
    if (introSection) {
      introSection.style.display = currentPage === 1 ? "block" : "none"
    }
  
    const startIndex = (currentPage - 1) * questionsPerPage
    const endIndex = Math.min(startIndex + questionsPerPage, ratingQuestions.length)
  
    for (let i = startIndex; i < endIndex; i++) {
      const question = ratingQuestions[i]
      const questionElement = createQuestionElement(question, i + 1)
      questionsContainer.appendChild(questionElement)
      questionRefs.push(questionElement)
    }
  
    // Highlight the active question
    highlightActiveQuestion()
  }
  
  // Create a question element based on its type
  function createQuestionElement(question, displayNumber) {
    const questionDiv = document.createElement("div")
    questionDiv.className = `question ${answers[question.id] ? "completed" : ""} ${activeQuestionId === question.id ? "active" : ""}`
    questionDiv.dataset.id = question.id
  
    // Question header with number and text
    const questionHeader = document.createElement("div")
    questionHeader.className = "question-header"
  
    const questionNumber = document.createElement("div")
    questionNumber.className = "question-number"
    questionNumber.textContent = displayNumber
  
    const questionText = document.createElement("div")
    questionText.className = "question-text"
    questionText.textContent = question.text
  
    if (question.required) {
      const requiredSpan = document.createElement("span")
      requiredSpan.className = "required"
      requiredSpan.textContent = " *"
      questionText.appendChild(requiredSpan)
    }
  
    questionHeader.appendChild(questionNumber)
    questionHeader.appendChild(questionText)
    questionDiv.appendChild(questionHeader)
  
    // Question content based on type
    const questionContent = document.createElement("div")
    questionContent.className = "question-content"
  
    if (question.type === "text") {
      const input = document.createElement("input")
      input.type = "text"
      input.className = "input-field"
      input.placeholder = question.placeholder || ""
      input.value = answers[question.id] || ""
  
      input.addEventListener("input", (e) => handleAnswerChange(question.id, e.target.value))
  
      questionContent.appendChild(input)
  
      if (question.helperText) {
        const helperText = document.createElement("div")
        helperText.className = "helper-text"
        helperText.textContent = question.helperText
        questionContent.appendChild(helperText)
      }
    } else if (question.type === "rating") {
      // Create a table-like structure for the rating options
      const ratingTable = document.createElement("div")
      ratingTable.className = "rating-table"
  
      // Create the header row with labels
      const headerRow = document.createElement("div")
      headerRow.className = "rating-row rating-header"
  
      ratingLabels.forEach((label) => {
        const headerCell = document.createElement("div")
        headerCell.className = "rating-cell"
        headerCell.innerHTML = `${label.value} = ${label.label}`
        headerRow.appendChild(headerCell)
      })
  
      ratingTable.appendChild(headerRow)
  
      // Create the options row
      const optionsRow = document.createElement("div")
      optionsRow.className = "rating-row"
  
      ratingLabels.forEach((label) => {
        const optionCell = document.createElement("div")
        optionCell.className = "rating-cell"
  
        const radioInput = document.createElement("input")
        radioInput.type = "radio"
        radioInput.name = `question-${question.id}`
        radioInput.value = label.value
        radioInput.id = `question-${question.id}-${label.value}`
        radioInput.checked = answers[question.id] === label.value
        radioInput.className = "rating-radio"
  
        radioInput.addEventListener("change", () => {
          if (radioInput.checked) {
            handleAnswerChange(question.id, label.value)
          }
        })
  
        optionCell.appendChild(radioInput)
        optionsRow.appendChild(optionCell)
      })
  
      ratingTable.appendChild(optionsRow)
      questionContent.appendChild(ratingTable)
    }
  
    questionDiv.appendChild(questionContent)
  
    return questionDiv
  }
  
  // Handle answer change
  function handleAnswerChange(questionId, value) {
    // Clear any previous errors
    hideAlert()
  
    // Update the answer
    answers[questionId] = value
    localStorage.setItem("teamRoleAnswers", JSON.stringify(answers))
  
    // Mark the question as completed
    const questionElement = document.querySelector(`.question[data-id="${questionId}"]`)
    if (questionElement) {
      questionElement.classList.add("completed")
    }
  
    // Update progress
    updateProgressBar()
  
    // Find next unanswered question on current page
    const currentPageQuestions = getCurrentPageQuestions()
    const currentIndex = currentPageQuestions.findIndex((q) => q.id === questionId)
  
    if (currentIndex < currentPageQuestions.length - 1) {
      // Move to next question on this page
      const nextQuestion = currentPageQuestions[currentIndex + 1]
      setActiveQuestion(nextQuestion.id)
    }
  
    // Update button states
    updateButtonStates()
  }
  
  // Get current page questions
  function getCurrentPageQuestions() {
    const startIndex = (currentPage - 1) * questionsPerPage
    return ratingQuestions.slice(startIndex, Math.min(startIndex + questionsPerPage, ratingQuestions.length))
  }
  
  // Set active question
  function setActiveQuestion(questionId) {
    activeQuestionId = questionId
    highlightActiveQuestion()
  
    // Scroll to the active question
    const activeQuestion = document.querySelector(`.question[data-id="${questionId}"]`)
    if (activeQuestion) {
      activeQuestion.scrollIntoView({ behavior: "smooth", block: "center" })
    }
  }
  
  // Highlight the active question
  function highlightActiveQuestion() {
    document.querySelectorAll(".question").forEach((q) => {
      q.classList.remove("active")
    })
  
    const activeQuestion = document.querySelector(`.question[data-id="${activeQuestionId}"]`)
    if (activeQuestion) {
      activeQuestion.classList.add("active")
    }
  }
  
  // Update progress bar
  function updateProgressBar() {
    const answeredCount = Object.keys(answers).length
    const totalQuestions = ratingQuestions.length
    const percent = totalQuestions > 0 ? (answeredCount / totalQuestions) * 100 : 0
  
    progressBar.style.width = `${percent}%`
    progressPercentage.textContent = `${Math.round(percent)}%`
  }
  
  // Update page indicator
  function updatePageIndicator() {
    pageIndicator.textContent = `Página ${currentPage} de ${totalPages}`
  }
  
  // Check if current page is complete
  function isCurrentPageComplete() {
    const currentPageQuestions = getCurrentPageQuestions()
    return currentPageQuestions.every((question) => {
      return answers[question.id] !== undefined && answers[question.id] !== ""
    })
  }
  
  // Check if all questions are answered
  function isFormComplete() {
    return ratingQuestions.every((question) => {
      return answers[question.id] !== undefined && answers[question.id] !== ""
    })
  }
  
  // Update button states
  function updateButtonStates() {
    prevButton.disabled = currentPage === 1
  
    if (currentPage < totalPages) {
      nextButton.textContent = "Siguiente"
      nextButton.className = "button button-primary"
      nextButton.disabled = !isCurrentPageComplete()
    } else {
      nextButton.textContent = "Finalizar"
      nextButton.className = "button button-success"
      nextButton.disabled = !isFormComplete()
    }
  }
  
  // Go to previous page
  function goToPrevPage() {
    if (currentPage > 1) {
      currentPage--
      renderCurrentPage()
      updatePageIndicator()
      updateButtonStates()
  
      // Set active question to first question on the page
      const firstQuestion = getCurrentPageQuestions()[0]
      if (firstQuestion) {
        setActiveQuestion(firstQuestion.id)
      }
  
      window.scrollTo(0, 0)
    }
  }
  
  // Handle next button click
  function handleNextButtonClick() {
    if (currentPage < totalPages) {
      goToNextPage()
    } else {
      submitForm()
    }
  }
  
  // Go to next page
  function goToNextPage() {
    if (currentPage < totalPages) {
      currentPage++
      renderCurrentPage()
      updatePageIndicator()
      updateButtonStates()
  
      // Set active question to first question on the page
      const firstQuestion = getCurrentPageQuestions()[0]
      if (firstQuestion) {
        setActiveQuestion(firstQuestion.id)
      }
  
      window.scrollTo(0, 0)
    }
  }
  
  // Submit the form
  function submitForm() {
    // Validate all answers one more time
    for (const question of ratingQuestions) {
      const answer = answers[question.id]
      if (answer === undefined || answer === "") {
        showAlert(`Por favor responda la pregunta ${question.id - 13}.`)
        return
      }
    }
  
    // Send the data to the server
    fetch("/student/submit_form2", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(answers),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Use a custom notification instead of alert
          showNotification(data.message)
  
          // Clear localStorage
          localStorage.removeItem("teamRoleAnswers")
  
          // Redirect to home page after a short delay
          setTimeout(() => {
            window.location.href = "/student/"
          }, 1500)
        } else {
          showAlert(data.message || "Error al enviar el formulario")
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        showAlert("Error al enviar el formulario. Por favor intente nuevamente.")
      })
  }
  
  // Show notification message
  function showNotification(message) {
    // Create notification element
    const notification = document.createElement("div")
    notification.className = "notification success"
    notification.innerHTML = `
          <div class="notification-content">
              <span class="notification-icon">✓</span>
              <span class="notification-message">${message}</span>
          </div>
      `
  
    // Add to document
    document.body.appendChild(notification)
  
    // Remove after 3 seconds
    setTimeout(() => {
      notification.classList.add("fade-out")
      setTimeout(() => {
        document.body.removeChild(notification)
      }, 300)
    }, 3000)
  }
  
  // Show alert message
  function showAlert(message) {
    alertMessage.textContent = message
    alertElement.classList.remove("hidden")
  }
  
  // Hide alert message
  function hideAlert() {
    alertElement.classList.add("hidden")
  }
  
  // Make closeAlert function available globally
  window.closeAlert = hideAlert
  
  // Initialize the form when the DOM is loaded
  document.addEventListener("DOMContentLoaded", initForm)
  
  