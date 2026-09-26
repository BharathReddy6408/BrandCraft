// static/js/chat/chat.js
document.addEventListener("DOMContentLoaded", function() {
    window.CopilotChat = {
        conversationId: null,
        isVoiceActive: false,
        
        init: function(chatUrl, csrfToken) {
            this.chatUrl = chatUrl;
            this.csrfToken = csrfToken;
            this.bindEvents();
        },
        
        bindEvents: function() {
            const input = document.getElementById('chatInput');
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.sendMessage();
                    }
                });
            }
            
            const micBtn = document.getElementById('micBtn');
            if (micBtn) {
                micBtn.addEventListener('click', () => {
                    this.toggleVoice();
                });
            }
            
            const speakerBtn = document.getElementById('speakerBtn');
            if (speakerBtn) {
                speakerBtn.addEventListener('click', () => {
                    this.isVoiceActive = !this.isVoiceActive;
                    if (this.isVoiceActive) {
                        speakerBtn.classList.add('text-primary');
                        speakerBtn.classList.remove('text-muted');
                    } else {
                        speakerBtn.classList.remove('text-primary');
                        speakerBtn.classList.add('text-muted');
                        window.speechSynthesis.cancel();
                    }
                });
            }
        },
        
        toggleChat: function() {
            const win = document.getElementById('aiChatWindow');
            if (win.style.display === 'none' || win.style.display === '') {
                win.style.display = 'flex';
                if(window.gsap) {
                    gsap.from(win, { duration: 0.3, y: 30, opacity: 0, ease: 'power2.out' });
                }
            } else {
                win.style.display = 'none';
            }
        },
        
        sendMessage: function(textOverride = null) {
            const input = document.getElementById('chatInput');
            const msgText = textOverride || input.value.trim();
            if (!msgText) return;
            
            this.appendMessage('user', msgText);
            
            if (!textOverride) {
                input.value = '';
            }
            
            const typingIndicator = this.appendTypingIndicator();
            
            // Dynamic Generation Status updates
            let progressInterval = setInterval(() => {
                const statuses = ["Analyzing business idea...", "Generating brand strategy...", "Developing visual identity...", "Building brand board...", "Finalizing assets..."];
                const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
                typingIndicator.innerHTML = `<span style="font-size: 0.8rem; font-style: italic;">${randomStatus}</span><span class="dots"><span>.</span><span>.</span><span>.</span></span>`;
            }, 3000);
            
            fetch(this.chatUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ 
                    message: msgText,
                    conversation_id: this.conversationId 
                })
            })
            .then(res => res.json())
            .then(data => {
                clearInterval(progressInterval);
                typingIndicator.remove();
                if (data.conversation_id) {
                    this.conversationId = data.conversation_id;
                }
                
                if (data.response_type === 'card' && data.content) {
                    this.appendCardMessage('ai', data.response, data.content, data.actions);
                } else if (data.response_type === 'image' && data.content && data.content.image_url) {
                    this.appendImageMessage('ai', data.response, data.content.image_url, data.actions);
                } else if (data.response_type === 'multi_asset' && data.content) {
                    this.appendMultiAssetMessage('ai', data.response, data.content, data.actions);
                } else {
                    this.appendMessage('ai', data.response, data.actions);
                }
                
                if (this.isVoiceActive) {
                    this.speak(data.response);
                }
            })
            .catch(err => {
                console.error(err);
                clearInterval(progressInterval);
                typingIndicator.remove();
                this.appendMessage('ai', "Error connecting to AI Copilot.");
            });
        },
        
        appendMessage: function(role, text, actions = []) {
            const body = document.getElementById('chatBody');
            const msgDiv = document.createElement('div');
            msgDiv.className = `chat-msg ${role === 'ai' ? 'assistant' : 'user'}`;
            msgDiv.innerHTML = text.replace(/\n/g, '<br>');
            
            if (actions && actions.length > 0) {
                const actionsDiv = document.createElement('div');
                actionsDiv.className = "mt-2 d-flex gap-2 flex-wrap";
                actions.forEach(action => {
                    const btn = document.createElement('button');
                    btn.className = "btn btn-sm btn-outline-dark rounded-pill";
                    btn.innerText = action.label;
                    if (action.type === 'navigate') {
                        btn.onclick = () => window.location.href = action.route;
                    }
                    actionsDiv.appendChild(btn);
                });
                msgDiv.appendChild(actionsDiv);
            }
            
            body.appendChild(msgDiv);
            body.scrollTop = body.scrollHeight;
        },
        
        appendCardMessage: function(role, fallbackText, contentData, actions = []) {
            const body = document.getElementById('chatBody');
            const msgDiv = document.createElement('div');
            msgDiv.className = `chat-msg assistant`;
            
            let cardHtml = `<div class="copilot-card">`;
            if (contentData.headline) {
                cardHtml += `<h6 class="fw-bold">${contentData.headline}</h6>`;
            }
            if (contentData.body) {
                cardHtml += `<p class="small text-muted mb-2">${contentData.body}</p>`;
            }
            if (contentData.cta) {
                cardHtml += `<div class="fw-bold small">CTA: ${contentData.cta}</div>`;
            }
            if (contentData.content) { // social media
                cardHtml += `<p class="small mb-1">${contentData.content}</p>`;
            }
            if (contentData.hashtags) {
                cardHtml += `<div class="small text-primary">${contentData.hashtags.join(' ')}</div>`;
            }
            cardHtml += `</div>`;
            
            msgDiv.innerHTML = cardHtml;
            
            if (actions && actions.length > 0) {
                const actionsDiv = document.createElement('div');
                actionsDiv.className = "mt-2 d-flex gap-2 flex-wrap";
                actions.forEach(action => {
                    const btn = document.createElement('button');
                    btn.className = "btn btn-sm btn-dark rounded-pill";
                    btn.innerText = action.label;
                    actionsDiv.appendChild(btn);
                });
                msgDiv.appendChild(actionsDiv);
            }
            
            body.appendChild(msgDiv);
            body.scrollTop = body.scrollHeight;
        },
        appendImageMessage: function(role, fallbackText, imageUrl, actions = []) {
            const body = document.getElementById('chatBody');
            const msgDiv = document.createElement('div');
            msgDiv.className = `chat-msg assistant`;
            
            let html = `<div class="copilot-card">`;
            if (fallbackText) {
                html += `<p class="small text-muted mb-2">${fallbackText}</p>`;
            }
            html += `<img src="${imageUrl}" alt="Generated Image" style="max-width: 100%; border-radius: 8px; margin-top: 8px;">`;
            html += `</div>`;
            
            msgDiv.innerHTML = html;
            
            if (actions && actions.length > 0) {
                const actionsDiv = document.createElement('div');
                actionsDiv.className = "mt-2 d-flex gap-2 flex-wrap";
                actions.forEach(action => {
                    const btn = document.createElement('button');
                    btn.className = "btn btn-sm btn-dark rounded-pill";
                    btn.innerText = action.label;
                    actionsDiv.appendChild(btn);
                });
                msgDiv.appendChild(actionsDiv);
            }
            
            body.appendChild(msgDiv);
            body.scrollTop = body.scrollHeight;
        },
        
        appendMultiAssetMessage: function(role, fallbackText, contentData, actions = []) {
            const body = document.getElementById('chatBody');
            const msgDiv = document.createElement('div');
            msgDiv.className = `chat-msg assistant w-100`;
            msgDiv.style.maxWidth = '100%';
            
            let html = `<div class="copilot-card">`;
            if (fallbackText) {
                html += `<p class="small mb-3 fw-bold">${fallbackText}</p>`;
            }
            
            const strategy = contentData.strategy;
            if (strategy) {
                if(strategy.business_name) html += `<div class="fw-bold fs-6 text-primary mb-1">${strategy.business_name}</div>`;
                if(strategy.tagline) html += `<div class="small fst-italic text-muted mb-2">${strategy.tagline}</div>`;
                
                html += `<div class="d-flex gap-2 mb-2">`;
                if (strategy.primary_color) {
                    html += `<div style="width:24px; height:24px; border-radius:4px; background-color:${strategy.primary_color}; border:1px solid #ccc;" title="Primary Color"></div>`;
                }
                if (strategy.secondary_color) {
                    html += `<div style="width:24px; height:24px; border-radius:4px; background-color:${strategy.secondary_color}; border:1px solid #ccc;" title="Secondary Color"></div>`;
                }
                html += `</div>`;
            }
            
            // Handle array of assets
            const assets = contentData.assets || contentData.visuals;
            if (Array.isArray(assets)) {
                html += `<div class="d-flex flex-wrap gap-2 mt-2">`;
                assets.forEach(asset => {
                    if (asset.status === 'SUCCESS' && asset.url) {
                        html += `<div class="border rounded p-1" style="width: 48%;">`;
                        html += `<div class="small fw-bold text-center mb-1 text-uppercase">${asset.type.replace('_', ' ')}</div>`;
                        html += `<img src="${asset.url}" alt="${asset.type}" style="width: 100%; border-radius: 4px;">`;
                        html += `</div>`;
                    } else {
                        html += `<div class="border rounded p-1 text-center text-muted small" style="width: 48%;">Failed to generate ${asset.type}</div>`;
                    }
                });
                html += `</div>`;
            }
            
            html += `</div>`;
            
            msgDiv.innerHTML = html;
            
            if (actions && actions.length > 0) {
                const actionsDiv = document.createElement('div');
                actionsDiv.className = "mt-2 d-flex gap-2 flex-wrap";
                actions.forEach(action => {
                    const btn = document.createElement('button');
                    btn.className = "btn btn-sm btn-dark rounded-pill";
                    btn.innerText = action.label;
                    if (action.type === 'navigate' && action.url) {
                        btn.onclick = () => window.location.href = action.url;
                    }
                    actionsDiv.appendChild(btn);
                });
                msgDiv.appendChild(actionsDiv);
            }
            
            body.appendChild(msgDiv);
            body.scrollTop = body.scrollHeight;
        },
        
        appendTypingIndicator: function() {
            const body = document.getElementById('chatBody');
            const typingMsg = document.createElement('div');
            typingMsg.className = 'chat-msg assistant typing';
            typingMsg.innerHTML = '<span class="dots"><span>.</span><span>.</span><span>.</span></span>';
            body.appendChild(typingMsg);
            body.scrollTop = body.scrollHeight;
            return typingMsg;
        },
        
        toggleVoice: function() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                alert("Voice input is not supported in your browser.");
                return;
            }
            
            const recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            
            const micBtn = document.getElementById('micBtn');
            micBtn.classList.add('text-danger');
            
            recognition.start();
            
            recognition.onresult = (event) => {
                const speechResult = event.results[0][0].transcript;
                document.getElementById('chatInput').value = speechResult;
                this.sendMessage(speechResult);
                micBtn.classList.remove('text-danger');
            };
            
            recognition.onspeechend = () => {
                recognition.stop();
                micBtn.classList.remove('text-danger');
            };
            
            recognition.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                micBtn.classList.remove('text-danger');
            };
        },
        
        speak: function(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                window.speechSynthesis.speak(utterance);
            }
        }
    };
});
