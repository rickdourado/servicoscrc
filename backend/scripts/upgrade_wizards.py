import os
import glob
import re

html_files = glob.glob('frontend/wireframes/tobe_*.html')

js_logic = """
        </div> <!-- End of step-content wrapper -->

        <div class="wizard-footer">
            <button class="btn btn-outline" id="btn-back" style="visibility: hidden;" onclick="prevStep()">Voltar</button>
            <button class="btn btn-primary" id="btn-next" onclick="nextStep()">Próximo Passo</button>
        </div>
    </div>

    <script>
        const steps = document.querySelectorAll('.step-content-section');
        const indicators = document.querySelectorAll('.step-indicator');
        const progressFill = document.querySelector('.stepper-progress-fill');
        const btnNext = document.getElementById('btn-next');
        const btnBack = document.getElementById('btn-back');
        let currentStep = 0;

        function updateStepper() {
            // Update Top Progress Bar & Indicators
            indicators.forEach((ind, index) => {
                ind.classList.remove('active', 'completed');
                if (index === currentStep) {
                    ind.classList.add('active');
                    ind.querySelector('.step-circle').innerHTML = index + 1;
                } else if (index < currentStep) {
                    ind.classList.add('completed');
                    ind.querySelector('.step-circle').innerHTML = '✓';
                } else {
                    ind.querySelector('.step-circle').innerHTML = index + 1;
                }
            });
            
            const progress = (currentStep / (indicators.length - 1)) * 100;
            progressFill.style.width = `${progress}%`;

            // Update Visibility
            steps.forEach((step, index) => {
                step.style.display = index === currentStep ? 'block' : 'none';
            });

            // Update Buttons
            btnBack.style.visibility = currentStep === 0 ? 'hidden' : 'visible';
            
            if (currentStep === steps.length - 1) {
                btnNext.innerHTML = 'Finalizar Chamado';
                btnNext.style.background = 'var(--success)';
            } else {
                btnNext.innerHTML = 'Próximo Passo 👉';
                btnNext.style.background = 'var(--primary)';
            }
        }

        function nextStep() {
            if (currentStep < steps.length - 1) {
                currentStep++;
                updateStepper();
            } else {
                alert('Chamado registrado com sucesso! (Fluxo Finalizado)');
            }
        }

        function prevStep() {
            if (currentStep > 0) {
                currentStep--;
                updateStepper();
            }
        }
        
        // Initialize
        updateStepper();
    </script>
</body>
</html>
"""

step1 = """
        <div class="step-content-section" id="step1">
            <h2 class="step-title">Onde é o local da ocorrência?</h2>
            <p class="step-subtitle">Forneça o endereço exato ou clique no mapa para marcar a localização.</p>

            <div class="form-group">
                <label class="form-label">Pesquisar Endereço <span class="req">*</span></label>
                <div style="display: flex; gap: 8px;">
                    <input type="text" class="form-control" placeholder="Ex: Av. Presidente Vargas, 1000">
                    <button class="btn btn-outline" style="padding: 0.875rem;">🔍</button>
                </div>
            </div>
            
            <div style="width: 100%; height: 220px; background: #e2e8f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 24px; border: 1px dashed #94a3b8; flex-direction: column; overflow: hidden; position: relative;">
                <!-- Mock Map visual -->
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.3; background-image: repeating-linear-gradient(45deg, #cbd5e1 25%, transparent 25%, transparent 75%, #cbd5e1 75%, #cbd5e1), repeating-linear-gradient(45deg, #cbd5e1 25%, var(--bg) 25%, var(--bg) 75%, #cbd5e1 75%, #cbd5e1); background-position: 0 0, 10px 10px; background-size: 20px 20px;"></div>
                <span style="font-size: 2.5rem; position: relative; z-index: 2; transform: translateY(-10px); color: #ef4444;">📍</span>
                <span style="color: #475569; font-weight: 600; font-size: 0.95rem; margin-top: 4px; position: relative; z-index: 2;">Avenida Presidente Vargas, 1000 - Centro</span>
            </div>
            
            <div class="checkbox-row" style="margin-bottom: 24px; display: flex; align-items: center; gap: 8px;">
                <input type="checkbox" id="logradouro-inexistente">
                <label for="logradouro-inexistente" style="font-size: 0.9rem; font-weight: 500;">O endereço não possui logradouro fixo oficial</label>
            </div>

            <div class="form-group">
                <label class="form-label">Ponto de Referência</label>
                <input type="text" class="form-control" placeholder="Perto da padaria, em frente à praça...">
            </div>
        </div>
"""

step3 = """
        <div class="step-content-section" id="step3" style="display: none;">
            <h2 class="step-title">Evidências e Fotos</h2>
            <p class="step-subtitle">As fotos nos ajudam a identificar o problema mais rapidamente. Você pode anexar até 3 imagens.</p>

            <div style="border: 2px dashed var(--primary); background: var(--primary-light); border-radius: 12px; padding: 3rem 2rem; text-align: center; cursor: pointer; transition: all 0.2s;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">📸</div>
                <h3 style="color: var(--primary); font-weight: 700; margin-bottom: 0.5rem;">Arraste suas fotos para cá</h3>
                <p style="color: var(--text-gray); font-size: 0.9rem;">ou clique para buscar no seu dispositivo<br>(Formatos: JPG, PNG • Max: 5MB)</p>
            </div>
        </div>
"""

step4 = """
        <div class="step-content-section" id="step4" style="display: none;">
            <h2 class="step-title">Finalizar Chamado</h2>
            <p class="step-subtitle">Quase lá! Como você prefere se identificar neste chamado?</p>

            <div class="form-group">
                <label class="form-label">Nível de Sigilo <span class="req">*</span></label>
                <select class="form-control">
                    <option selected>Público - Quero acompanhar com meus dados</option>
                    <option>Sigiloso - Meus dados ficam restritos ao órgão</option>
                    <option>Anônimo - Não desejo me identificar</option>
                </select>
            </div>

            <div class="form-group">
                <label class="form-label">Telefone / WhatsApp</label>
                <input type="text" class="form-control" placeholder="(21) 90000-0000">
            </div>

            <div class="form-group">
                <label class="form-label">E-mail para acompanhamento</label>
                <input type="email" class="form-control" placeholder="seu.email@exemplo.com">
            </div>
            
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; padding: 1rem; border-radius: 8px; margin-top: 1.5rem;">
                <p style="color: #065f46; font-size: 0.85rem; font-weight: 600; line-height: 1.4;">Ao clicar em "Finalizar", este chamado será enviado diretamente para a Guarda Municipal / Órgão Responsável.</p>
            </div>
        </div>
"""

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already upgraded
    if 'id="btn-back"' in content:
        print(f"Skipping {filepath}, already has interactive logic.")
        continue
        
    # Replace the <div class="step-content"> to be <div class="step-content-wrapper" style="padding: 2.5rem 2rem;">
    # Then wrap the original step-content directly into id="step2"
    
    # 1. Update indicator class active state dynamically relying purely on JS
    content = re.sub(r'<div class="step-indicator completed">', '<div class="step-indicator">', content)
    content = re.sub(r'<div class="step-indicator active">', '<div class="step-indicator">', content)
    content = re.sub(r'<div class="stepper-progress-fill"></div>', '<div class="stepper-progress-fill" style="width: 0%; transition: width 0.3s ease;"></div>', content)
    
    # 2. Extract step 2 content
    # It starts at <div class="step-content"> and goes until <div class="wizard-footer">
    match = re.search(r'<div class="step-content">(.*?)<div class="wizard-footer">', content, re.DOTALL)
    if not match:
        continue
        
    original_step2 = match.group(1).strip()
    
    # Format the new body
    new_body = f"""
        <div class="step-content-wrapper" style="padding: 2.5rem 2rem;">
            {step1}
            <div class="step-content-section" id="step2" style="display: none;">
                {original_step2}
            </div>
            {step3}
            {step4}
    """
    
    # Replace from <div class="step-content"> to end of file with new body + js_logic
    
    new_content = content[:match.start()] + new_body + js_logic
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Upgraded {filepath}")
