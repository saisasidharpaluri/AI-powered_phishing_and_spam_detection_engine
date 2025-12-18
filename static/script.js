let currentType = 'email';

function switchType(type) {
    currentType = type;
    
    const emailBtn = document.getElementById('emailBtn');
    const urlBtn = document.getElementById('urlBtn');
    const inputText = document.getElementById('inputText');
    
    if (type === 'email') {
        emailBtn.classList.add('active');
        urlBtn.classList.remove('active');
        inputText.placeholder = 'Enter email body for analysis...';
    } else {
        urlBtn.classList.add('active');
        emailBtn.classList.remove('active');
        inputText.placeholder = 'Enter suspicious URL for analysis...';
    }
    
    // Hide result when switching types
    document.getElementById('result').style.display = 'none';
}

async function analyze() {
    const inputText = document.getElementById('inputText').value.trim();
    
    if (!inputText) {
        alert('Please enter some text or URL to analyze');
        return;
    }
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                input_text: inputText,
                input_type: currentType
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else {
            displayResult(data);
        }
        
    } catch (error) {
        showError('Failed to analyze. Please try again.');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Threat';
    }
}

function displayResult(data) {
    const resultSection = document.getElementById('result');
    const errorMsg = document.getElementById('errorMsg');
    
    errorMsg.style.display = 'none';
    resultSection.style.display = 'block';
    
    // Animate security score
    const scoreValue = document.getElementById('scoreValue');
    const scoreCircle = document.getElementById('scoreCircle');
    const score = data.security_score;
    
    animateScore(scoreValue, score);
    
    // Update circle progress
    const circumference = 534;
    const offset = circumference - (score / 100) * circumference;
    scoreCircle.style.strokeDashoffset = offset;
    
    // Update circle color based on score
    const circleContainer = scoreCircle.parentElement.parentElement;
    circleContainer.className = 'score-circle';
    if (score < 40) {
        circleContainer.classList.add('danger');
    } else if (score < 70) {
        circleContainer.classList.add('warning');
    }
    
    // Update threat level
    document.getElementById('threatLevel').textContent = data.threat_level;
    
    // Update classification
    const classification = data.is_malicious ? '⚠️ MALICIOUS' : '✅ SAFE';
    const classificationEl = document.getElementById('classification');
    classificationEl.textContent = classification;
    classificationEl.style.color = data.is_malicious ? '#c62828' : '#2e7d32';
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function animateScore(element, targetScore) {
    let currentScore = 0;
    const increment = targetScore / 50;
    const interval = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(interval);
        }
        element.textContent = Math.round(currentScore) + '%';
    }, 20);
}

function showError(message) {
    const resultSection = document.getElementById('result');
    const errorMsg = document.getElementById('errorMsg');
    
    resultSection.style.display = 'block';
    errorMsg.style.display = 'block';
    errorMsg.textContent = message;
    
    // Hide other result elements
    document.querySelector('.security-score-container').style.display = 'none';
    document.querySelector('.threat-info').style.display = 'none';
}
