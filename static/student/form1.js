// Personality types for question 2
const personalityTypes = [
    { value: "INTJ", label: "INTJ - Arquitecto" },
    { value: "INTP", label: "INTP - Lógico" },
    { value: "ENTJ", label: "ENTJ - Comandante" },
    { value: "ENTP", label: "ENTP - Innovador" },
    { value: "INFJ", label: "INFJ - Abogado" },
    { value: "INFP", label: "INFP - Mediador" },
    { value: "ENFJ", label: "ENFJ - Protagonista" },
    { value: "ENFP", label: "ENFP - Activista" },
    { value: "ISTJ", label: "ISTJ - Logista" },
    { value: "ISFJ", label: "ISFJ - Defensor" },
    { value: "ESTJ", label: "ESTJ - Ejecutivo" },
    { value: "ESFJ", label: "ESFJ - Cónsul" },
    { value: "ISTP", label: "ISTP - Virtuoso" },
    { value: "ISFP", label: "ISFP - Aventurero" },
    { value: "ESTP", label: "ESTP - Emprendedor" },
    { value: "ESFP", label: "ESFP - Animador" },
  ]
  
  // Initial questions from the mockup
  const initialQuestions = [//no
    {
      id: 1,
      text: "Según el resultado del test de la pagina https://www.16personalities.com/es/test-de-personalidad ¿Cuál es tu tipo de personalidad?",
      type: "radio",
      options: personalityTypes,
      required: true,
    },
    {
      id: 2,
      text: '¿Con cuál letra termina, A o T? Ejemplo: Si tus resultados fueron ISFP-T significa que en la anterior pregunta respondiste "ISFP - Aventurero" y en esta pregunta colocarías la letra T',
      type: "radio",
      options: [
        { value: "A", label: "A" },
        { value: "T", label: "T" },
      ],
      required: true,
    },
    {
      id: 3,
      text: "Según los resultados: ¿eres extrovertido o Introvertido?",
      type: "radio",
      options: [
        { value: "extrovertido", label: "Extrovertido" },
        { value: "introvertido", label: "Introvertido" },
      ],
      required: true,
    },
    {
      id: 4,
      text: "¿Cuál fue el porcentaje? Ingrese solo el número. Ej: Si tu resultado fue Extravertido 60% solo digita 60.",
      type: "text",
      placeholder: "Ingresa el porcentaje",
      helperText: "El número debe estar comprendido entre 0 y 100",
      required: true,
      numeric: true,
      min: 0,
      max: 100,
    },
    {
      id: 5,
      text: "Según los resultados: ¿eres Intuitivo o Observador?",
      type: "radio",
      options: [
        { value: "intuitivo", label: "Intuitivo" },
        { value: "observador", label: "Observador" },
      ],
      required: true,
    },
    {
      id: 6,
      text: "¿Cuál fue el porcentaje? Ingrese solo el número. Ej: Si tu resultado fue Intuitivo 75% solo digita 75.",
      type: "text",
      placeholder: "Ingresa el porcentaje",
      helperText: "El número debe estar comprendido entre 0 y 100",
      required: true,
      numeric: true,
      min: 0,
      max: 100,
    },
    {
      id: 7,
      text: "Según los resultados: ¿eres Pensamiento o Emocional?",
      type: "radio",
      options: [
        { value: "pensamiento", label: "Pensamiento" },
        { value: "emocional", label: "Emocional" },
      ],
      required: true,
    },
    {
      id: 8,
      text: "¿Cuál fue el porcentaje? Ingrese solo el número. Ej: Si tu resultado fue Emocional 56% solo digita 56.",
      type: "text",
      placeholder: "Ingresa el porcentaje",
      helperText: "El número debe estar comprendido entre 0 y 100",
      required: true,
      numeric: true,
      min: 0,
      max: 100,
    },
    {
      id: 9,
      text: "Según los resultados: ¿eres Juzgador o Prospección?",
      type: "radio",
      options: [
        { value: "juzgador", label: "Juzgador" },
        { value: "prospeccion", label: "Prospección" },
      ],
      required: true,
    },
    {
      id: 10,
      text: "¿Cuál fue el porcentaje? Ingrese solo el número. Ej: Si tu resultado fue Juzgador 52% solo digita 52.",
      type: "text",
      placeholder: "Ingresa el porcentaje",
      helperText: "El número debe estar comprendido entre 0 y 100",
      required: true,
      numeric: true,
      min: 0,
      max: 100,
    },
    {
      id: 11,
      text: "Según los resultados: ¿eres Asertivo o Cauteloso?",
      type: "radio",
      options: [
        { value: "asertivo", label: "Asertivo" },
        { value: "cauteloso", label: "Cauteloso" },
      ],
      required: true,
    },
    {
      id: 12,
      text: "¿Cuál fue el porcentaje? Ingrese solo el número. Ej: Si tu resultado fue Asertivo 80% solo digita 80.",
      type: "text",
      placeholder: "Ingresa el porcentaje",
      helperText: "El número debe estar comprendido entre 0 y 100",
      required: true,
      numeric: true,
      min: 0,
      max: 100,
    },
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
  let activeQuestionId = 1
  let questionRefs = []
  
  // Constants
  const questionsPerPage = 10
  const totalPages = Math.ceil(initialQuestions.length / questionsPerPage)
  
  // Initialize the form
  function initForm() {
    // Try to load saved answers from localStorage
    const savedAnswers = localStorage.getItem("personalityTypeAnswers")
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
    const endIndex = Math.min(startIndex + questionsPerPage, initialQuestions.length)
  
    for (let i = startIndex; i < endIndex; i++) {
      const question = initialQuestions[i]
      const questionElement = createQuestionElement(question)
      questionsContainer.appendChild(questionElement)
      questionRefs.push(questionElement)
    }
  
    // Highlight the active question
    highlightActiveQuestion()
  }
  
  // Create a question element based on its type
  function createQuestionElement(question) {
    const questionDiv = document.createElement("div")
    questionDiv.className = `question ${answers[question.id] ? "completed" : ""} ${activeQuestionId === question.id ? "active" : ""}`
    questionDiv.dataset.id = question.id
  
    // Question header with number and text
    const questionHeader = document.createElement("div")
    questionHeader.className = "question-header"
  
    const questionNumber = document.createElement("div")
    questionNumber.className = "question-number"
    questionNumber.textContent = question.id
  
    const questionText = document.createElement("div")
    questionText.className = "question-text"
  
    // Special handling for question 2 to make the URL clickable
    if (question.id === 2) {
      // Split the text to isolate the URL
      const textParts = question.text.split("https://")
      const beforeUrl = textParts[0]
      const urlAndAfter = "https://" + textParts[1]
  
      // Find where the URL ends (at the first space)
      const spaceIndex = urlAndAfter.indexOf(" ")
      const url = urlAndAfter.substring(0, spaceIndex)
      const afterUrl = urlAndAfter.substring(spaceIndex)
  
      // Set the text content with the URL as a link
      questionText.innerHTML = beforeUrl
  
      const link = document.createElement("a")
      link.href = url
      link.textContent = url
      link.target = "_blank" // Open in new tab
      questionText.appendChild(link)
  
      questionText.innerHTML += afterUrl
    } else {
      questionText.textContent = question.text
    }
  
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
      input.type = question.numeric ? "number" : "text"
      input.className = "input-field"
      input.placeholder = question.placeholder || ""
      input.value = answers[question.id] || ""
      if (question.min !== undefined) input.min = question.min
      if (question.max !== undefined) input.max = question.max
  
      input.addEventListener("input", (e) => handleAnswerChange(question.id, e.target.value))
  
      questionContent.appendChild(input)
  
      if (question.helperText) {
        const helperText = document.createElement("div")
        helperText.className = "helper-text"
        helperText.textContent = question.helperText
        questionContent.appendChild(helperText)
      }
    } else if (question.type === "radio") {
      const radioGroup = document.createElement("div")
      radioGroup.className = "radio-group"
  
      question.options.forEach((option) => {
        const radioOption = document.createElement("div")
        radioOption.className = "radio-option"
  
        const radioInput = document.createElement("input")
        radioInput.type = "radio"
        radioInput.name = `question-${question.id}`
        radioInput.value = option.value
        radioInput.id = `question-${question.id}-${option.value}`
        radioInput.checked = answers[question.id] === option.value
  
        radioInput.addEventListener("change", () => {
          if (radioInput.checked) {
            handleAnswerChange(question.id, option.value)
          }
        })
  
        const radioLabel = document.createElement("label")
        radioLabel.className = "radio-label"
        radioLabel.htmlFor = `question-${question.id}-${option.value}`
        radioLabel.textContent = option.label
  
        radioOption.appendChild(radioInput)
        radioOption.appendChild(radioLabel)
        radioGroup.appendChild(radioOption)
      })
  
      questionContent.appendChild(radioGroup)
    }
  
    questionDiv.appendChild(questionContent)
  
    return questionDiv
  }
  
  // Handle answer change
  function handleAnswerChange(questionId, value) {
    const question = initialQuestions.find((q) => q.id === questionId)
    if (!question) return
  
    // Validate the answer
    if (!validateAnswer(question, value)) {
      return
    }
  
    // Clear any previous errors
    hideAlert()
  
    // Update the answer
    answers[questionId] = value
    localStorage.setItem("personalityTypeAnswers", JSON.stringify(answers))
  
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
  
  // Validate answer based on question type
  function validateAnswer(question, value) {
    if (value === "") return false
  
    if (question.type === "text") {
      if (question.numeric) {
        // Check if the value is a number and within range if specified
        if (!/^\d+$/.test(value)) {
          showAlert(`La pregunta ${question.id} requiere un valor numérico.`)
          return false
        }
  
        const numValue = Number.parseInt(value)
        if (question.min !== undefined && numValue < question.min) {
          showAlert(`El valor debe ser mayor o igual a ${question.min}.`)
          return false
        }
        if (question.max !== undefined && numValue > question.max) {
          showAlert(`El valor debe ser menor o igual a ${question.max}.`)
          return false
        }
      }
    }
  
    return true
  }
  
  // Get current page questions
  function getCurrentPageQuestions() {
    const startIndex = (currentPage - 1) * questionsPerPage
    return initialQuestions.slice(startIndex, Math.min(startIndex + questionsPerPage, initialQuestions.length))
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
    const totalQuestions = initialQuestions.length
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
    return initialQuestions.every((question) => {
      return answers[question.id] !== undefined && answers[question.id] !== ""
    })
  }
  
  // Update button states
  function updateButtonStates() {
    prevButton.disabled = currentPage === 1
  
    if (currentPage < totalPages) {
      nextButton.textContent = "Siguiente"
      nextButton.className = "button"
      nextButton.disabled = !isCurrentPageComplete()
    } else {
      nextButton.textContent = "Finalizar"
      nextButton.className = "button"
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
    for (const question of initialQuestions) {
      const answer = answers[question.id]
      if (answer === undefined || answer === "") {
        showAlert(`Por favor responda la pregunta ${question.id}.`)
        return
      }
  
      if (!validateAnswer(question, answer)) {
        return
      }
    }
  
    // Send the data to the server
    fetch("/student/submit_form1", {
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
          localStorage.removeItem("personalityTypeAnswers")
  
          // Redirect to home page after a short delay
          setTimeout(() => {
            window.location.href = "/student"
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