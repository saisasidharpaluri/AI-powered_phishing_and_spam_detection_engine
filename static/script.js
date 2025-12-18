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
        showError('⚠️ Please enter some text or URL to analyze');
        return;
    }
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    const originalText = analyzeBtn.textContent;
    analyzeBtn.disabled = true;
    analyzeBtn.classList.add('loading');
    analyzeBtn.textContent = 'Analyzing...';
    
    // Hide previous results
    document.getElementById('result').style.display = 'none';
    
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
        
        if (!response.ok) {
            throw new Error('Server error');
        }
        
        const data = await response.json();
        
        if (data.error) {
            showError('❌ ' + data.error);
        } else {
            displayResult(data);
        }
        
    } catch (error) {
        showError('❌ Failed to analyze. Please ensure the model is trained and try again.');
        console.error('Analysis error:', error);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove('loading');
        analyzeBtn.textContent = originalText;
    }
}

function displayResult(data) {
    const resultSection = document.getElementById('result');
    const errorMsg = document.getElementById('errorMsg');
    
    errorMsg.style.display = 'none';
    document.querySelector('.security-score-container').style.display = 'flex';
    document.querySelector('.threat-info').style.display = 'flex';
    resultSection.style.display = 'block';
    
    // Animate security score
    const scoreValue = document.getElementById('scoreValue');
    const scoreCircle = document.getElementById('scoreCircle');
    const score = data.security_score;
    
    // Reset animation
    scoreCircle.style.strokeDashoffset = 565;
    
    setTimeout(() => {
        animateScore(scoreValue, score);
        
        // Update circle progress (circumference = 2 * π * r = 2 * π * 90)
        const circumference = 565;
        const offset = circumference - (score / 100) * circumference;
        scoreCircle.style.strokeDashoffset = offset;
    }, 100);
    
    // Update circle color based on score
    const circleContainer = scoreCircle.parentElement.parentElement;
    circleContainer.className = 'score-circle';
    if (score < 40) {
        circleContainer.classList.add('danger');
    } else if (score < 70) {
        circleContainer.classList.add('warning');
    }
    
    // Update threat level
    const threatLevelEl = document.getElementById('threatLevel');
    threatLevelEl.textContent = data.threat_level;
    
    // Update classification with better styling
    const classification = data.is_malicious ? '🚨 MALICIOUS' : '✅ SAFE';
    const classificationEl = document.getElementById('classification');
    classificationEl.textContent = classification;
    classificationEl.style.color = data.is_malicious ? '#dc2626' : '#059669';
    classificationEl.style.fontWeight = '800';
    
    // Scroll to result
    setTimeout(() => {
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 200);
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
    errorMsg.style.animation = 'shake 0.5s';
    
    // Hide other result elements
    document.querySelector('.security-score-container').style.display = 'none';
    document.querySelector('.threat-info').style.display = 'none';
    
    // Scroll to error
    errorMsg.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Remove animation after it completes
    setTimeout(() => {
        errorMsg.style.animation = '';
    }, 500);
}
