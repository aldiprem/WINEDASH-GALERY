/* ===== RESET & VARIABLES ===== */
:root {
    --tg-bg: transparent;
    --tg-surface: rgba(31, 44, 51, 0.8);
    --tg-primary: #8774E1;
    --tg-primary-light: #9f8ee9;
    --tg-text: #ffffff;
    --tg-text-secondary: rgba(255, 255, 255, 0.6);
    --tg-text-hint: rgba(255, 255, 255, 0.4);
    --tg-accent-green: #3fcb95;
    --glass-bg: rgba(31, 44, 51, 0.72);
    --glossy-border: rgba(255, 255, 255, 0.08);
    --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
    --blur-amount: 20px;
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --radius-sm: 12px;
    --radius-md: 18px;
    --radius-lg: 24px;
    --radius-xl: 32px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

body, html {
    width: 100%;
    height: 100%;
    background: transparent !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    overflow-x: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--tg-text);
}

/* ===== CONTAINER ===== */
.tgs-container {
    width: 100%;
    max-width: 512px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 24px;
    background: transparent !important;
}

/* ===== STICKER WRAPPER ===== */
.sticker-wrapper {
    width: 100%;
    aspect-ratio: 1;
    position: relative;
    background: transparent !important;
    border-radius: 32px;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    border: 1px solid var(--glossy-border);
}

#tgs-player {
    width: 100%;
    height: 100%;
    background: transparent !important;
}

/* Pastikan Lottie Player transparan */
lottie-player {
    background: transparent !important;
}

/* ===== LOADING INDICATOR ===== */
.loading-indicator {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(10, 15, 20, 0.8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    z-index: 10;
    transition: opacity 0.3s ease;
    border-radius: 32px;
}

.loading-indicator.hidden {
    opacity: 0;
    pointer-events: none;
}

.loading-spinner {
    width: 48px;
    height: 48px;
    border: 4px solid rgba(135, 116, 225, 0.2);
    border-top-color: var(--tg-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.loading-text {
    color: var(--tg-text-secondary);
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.5px;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ===== ERROR MESSAGE ===== */
.error-message {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(244, 67, 54, 0.15);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    z-index: 20;
    border-radius: 32px;
    color: #ff6b6b;
    text-align: center;
    padding: 20px;
}

.error-message svg {
    opacity: 0.8;
}

.error-message div {
    font-size: 16px;
    font-weight: 600;
}

/* ===== GIFT INFO PANEL ===== */
.gift-info-panel {
    width: 100%;
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur-amount));
    -webkit-backdrop-filter: blur(var(--blur-amount));
    border: 1px solid var(--glossy-border);
    border-radius: 24px;
    padding: 20px;
    box-shadow: var(--glass-shadow);
}

.gift-title {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--glossy-border);
}

.gift-name {
    font-size: 24px;
    font-weight: 800;
    background: linear-gradient(135deg, #8774E1, #B583E3, #3fcb95);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

.gift-number {
    font-size: 18px;
    font-weight: 600;
    color: var(--tg-text-secondary);
}

.gift-attributes {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
}

.attribute-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 16px;
    border: 1px solid var(--glossy-border);
}

.attribute-label {
    color: var(--tg-text-hint);
    font-size: 14px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.attribute-value {
    display: flex;
    align-items: center;
    gap: 8px;
}

.attribute-name {
    color: white;
    font-size: 15px;
    font-weight: 600;
}

.attribute-rarity {
    font-size: 12px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    background: rgba(0, 0, 0, 0.3);
}

.attribute-rarity.rare {
    color: #ffd700;
    border: 1px solid rgba(255, 215, 0, 0.3);
}

.attribute-rarity.epic {
    color: #ff6b9d;
    border: 1px solid rgba(255, 107, 157, 0.3);
}

.attribute-rarity.legendary {
    color: #b86bff;
    border: 1px solid rgba(184, 107, 255, 0.3);
}

/* Skeleton loading */
.attribute-skeleton {
    height: 52px;
    background: linear-gradient(90deg, 
        rgba(255,255,255,0.05) 25%, 
        rgba(255,255,255,0.1) 50%, 
        rgba(255,255,255,0.05) 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: 16px;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.gift-availability {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: rgba(63, 203, 149, 0.1);
    border: 1px solid rgba(63, 203, 149, 0.2);
    border-radius: 20px;
    font-size: 14px;
    color: var(--tg-accent-green);
}

.availability-label {
    color: var(--tg-text-hint);
}

.availability-value {
    font-weight: 700;
}

/* ===== ACTION BUTTONS ===== */
.action-buttons {
    width: 100%;
    display: flex;
    gap: 12px;
}

.action-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px 16px;
    border-radius: 30px;
    font-weight: 600;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    text-decoration: none;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--glossy-border);
    color: var(--tg-text);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

.action-btn.primary {
    background: var(--tg-primary);
    border: none;
    color: white;
    box-shadow: 0 8px 20px rgba(135, 116, 225, 0.3);
}

.action-btn.primary:hover {
    background: var(--tg-primary-light);
    transform: translateY(-2px);
    box-shadow: 0 12px 25px rgba(135, 116, 225, 0.5);
}

.action-btn.secondary:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
}

.action-btn:active {
    transform: translateY(0);
}

.action-btn svg {
    width: 18px;
    height: 18px;
}

/* ===== TELEGRAM THEME ADAPTATION ===== */
@media (prefers-color-scheme: light) {
    :root {
        --tg-surface: rgba(255, 255, 255, 0.8);
        --tg-text: #000000;
        --tg-text-secondary: rgba(0, 0, 0, 0.6);
        --tg-text-hint: rgba(0, 0, 0, 0.4);
        --glass-bg: rgba(255, 255, 255, 0.72);
    }
    
    .attribute-name {
        color: #000000;
    }
    
    .gift-number {
        color: rgba(0, 0, 0, 0.5);
    }
    
    .attribute-item {
        background: rgba(0, 0, 0, 0.02);
    }
}

/* ===== RESPONSIVE ===== */
@media (max-width: 480px) {
    .tgs-container {
        padding: 16px;
        gap: 16px;
    }
    
    .gift-name {
        font-size: 20px;
    }
    
    .gift-number {
        font-size: 16px;
    }
    
    .attribute-label {
        font-size: 12px;
    }
    
    .attribute-name {
        font-size: 13px;
    }
    
    .attribute-rarity {
        font-size: 10px;
        padding: 3px 8px;
    }
    
    .action-btn {
        padding: 12px 12px;
        font-size: 13px;
    }
}
