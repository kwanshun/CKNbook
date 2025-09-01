// Frontend JavaScript for Tone-Toner

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('toneForm');
    const loading = document.getElementById('loading');
    const outputSection = document.getElementById('outputSection');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(form);
        const data = {
            paragraph: formData.get('paragraph'),
            tone: formData.get('tone'),
            language: formData.get('language')
        };

        // Validate inputs
        if (!data.paragraph || !data.tone || !data.language) {
            alert('請填寫所有必要欄位');
            return;
        }

        // Show loading, hide output
        loading.classList.remove('hidden');
        outputSection.classList.add('hidden');

        try {
            // Send request to backend
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                // Parse the result and display outputs
                parseAndDisplayResult(result.result);
                outputSection.classList.remove('hidden');
            } else {
                alert(result.error || '處理時發生錯誤');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('網路錯誤，請稍後再試');
        } finally {
            loading.classList.add('hidden');
        }
    });
});

function parseAndDisplayResult(resultText) {
    console.log('Parsing result:', resultText);
    
    // If there's an error message, show it in all outputs
    if (resultText.includes('錯誤:')) {
        document.getElementById('output1').textContent = resultText;
        document.getElementById('output2').textContent = resultText;
        document.getElementById('output3').textContent = resultText;
        return;
    }
    
    // Split the result into three options
    const lines = resultText.split('\n');
    let option1 = '';
    let option2 = '';
    let option3 = '';
    let currentOption = 0;

    for (let line of lines) {
        if (line.includes('選項1') || line.includes('選項 1') || line.includes('Option 1')) {
            currentOption = 1;
            // Extract content after the label
            const content = line.replace(/.*選項\s*1\s*[:：]?\s*/, '').trim();
            if (content) option1 += content + '\n';
        } else if (line.includes('選項2') || line.includes('選項 2') || line.includes('Option 2')) {
            currentOption = 2;
            const content = line.replace(/.*選項\s*2\s*[:：]?\s*/, '').trim();
            if (content) option2 += content + '\n';
        } else if (line.includes('選項3') || line.includes('選項 3') || line.includes('Option 3')) {
            currentOption = 3;
            const content = line.replace(/.*選項\s*3\s*[:：]?\s*/, '').trim();
            if (content) option3 += content + '\n';
        } else if (line.trim() !== '' && !line.includes('Instructions') && !line.includes('Analyze')) {
            if (currentOption === 1) {
                option1 += line + '\n';
            } else if (currentOption === 2) {
                option2 += line + '\n';
            } else if (currentOption === 3) {
                option3 += line + '\n';
            }
        }
    }

    // Fallback: if no options found, try to split by numbers or common patterns
    if (!option1 && !option2 && !option3) {
        const segments = resultText.split(/\d+[\.、:\s]/).filter(s => s.trim());
        if (segments.length >= 3) {
            option1 = segments[0] || '';
            option2 = segments[1] || '';
            option3 = segments[2] || '';
        } else {
            // If all else fails, show the raw response
            option1 = resultText;
            option2 = '無法解析第二個選項';
            option3 = '無法解析第三個選項';
        }
    }

    // Update the output divs
    document.getElementById('output1').textContent = option1.trim() || '生成中發生錯誤';
    document.getElementById('output2').textContent = option2.trim() || '生成中發生錯誤';
    document.getElementById('output3').textContent = option3.trim() || '生成中發生錯誤';
}

function copyText(outputId) {
    const outputElement = document.getElementById(outputId);
    const text = outputElement.textContent;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showCopyFeedback(outputId);
        }).catch(err => {
            console.error('複製失敗:', err);
            fallbackCopyText(text);
        });
    } else {
        fallbackCopyText(text);
    }
}

function fallbackCopyText(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopyFeedback();
    } catch (err) {
        console.error('複製失敗:', err);
        alert('複製失敗，請手動選取文字');
    }
    
    document.body.removeChild(textArea);
}

function showCopyFeedback(outputId) {
    const copyBtn = document.querySelector(`#${outputId}`).parentElement.querySelector('.copy-btn');
    const originalText = copyBtn.textContent;
    copyBtn.textContent = '已複製!';
    copyBtn.style.background = '#34c759';
    copyBtn.style.borderColor = '#34c759';
    copyBtn.style.color = 'white';
    
    setTimeout(() => {
        copyBtn.textContent = originalText;
        copyBtn.style.background = 'transparent';
        copyBtn.style.borderColor = '#007aff';
        copyBtn.style.color = '#007aff';
    }, 2000);
}
