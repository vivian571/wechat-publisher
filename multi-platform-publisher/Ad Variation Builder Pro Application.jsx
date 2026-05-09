import React, { useState, useCallback, useMemo } from 'react';
import { useDropzone } from 'react-dropzone';
import { ArrowUpTrayIcon, PhotoIcon, DocumentTextIcon, XMarkIcon, ArrowDownTrayIcon } from '@heroicons/react/24/solid';
/*
 The JSZip and FileSaver libraries are expected to be available in the global scope (window).
 In the execution environment, they are loaded via script tags.
 We access them using window.JSZip and window.saveAs.
*/

// --- Helper Components ---

const UploadPlaceholder = ({ icon, title, description }) => (
    <div className="text-center p-6 border-2 border-dashed border-gray-600 rounded-lg">
        {icon}
        <h3 className="mt-2 text-sm font-semibold text-gray-300">{title}</h3>
        <p className="mt-1 text-sm text-gray-500">{description}</p>
    </div>
);

const Spinner = () => (
    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
);

// --- Main Application ---

export default function App() {
    // --- State Management ---
    const [sampleAd, setSampleAd] = useState(null);
    const [productImages, setProductImages] = useState([]);
    const [promptsText, setPromptsText] = useState('');
    const [generatedImages, setGeneratedImages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [currentTask, setCurrentTask] = useState('');

    // --- Memoized Previews ---
    const sampleAdPreview = useMemo(() => sampleAd ? URL.createObjectURL(sampleAd) : null, [sampleAd]);
    const productImagesPreview = useMemo(() => productImages.map(file => ({
        ...file,
        preview: URL.createObjectURL(file)
    })), [productImages]);

    // --- File to Base64 Converter ---
    const fileToBase64 = (file) => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
    });

    // --- Dropzone Handlers ---
    const onDropSampleAd = useCallback(acceptedFiles => {
        if (acceptedFiles.length > 0) {
            setSampleAd(acceptedFiles[0]);
            setError(null);
        }
    }, []);

    const onDropProductImages = useCallback(acceptedFiles => {
        setProductImages(prev => [...prev, ...acceptedFiles]);
        setPromptsText(''); // Clear text prompts when images are added
        setError(null);
    }, []);

    const { getRootProps: getSampleAdRootProps, getInputProps: getSampleAdInputProps } = useDropzone({
        onDrop: onDropSampleAd,
        accept: { 'image/*': [] },
        maxFiles: 1
    });

    const { getRootProps: getProductImagesRootProps, getInputProps: getProductImagesInputProps } = useDropzone({
        onDrop: onDropProductImages,
        accept: { 'image/*': [] }
    });

    // --- Input and State Change Handlers ---
    const handleTextChange = (e) => {
        setPromptsText(e.target.value);
        if (e.target.value) {
            setProductImages([]); // Clear product images when text is typed
        }
        setError(null);
    };

    const removeProductImage = (index) => {
        setProductImages(prev => prev.filter((_, i) => i !== index));
    };

    // --- Core Generation Logic ---
    const handleGenerate = async () => {
        // 1. Validation
        if (!sampleAd) {
            setError('Please upload a sample ad poster.');
            return;
        }
        const useTextPrompts = promptsText.trim().length > 0;
        const useImagePrompts = productImages.length > 0;

        if (useTextPrompts && useImagePrompts) {
            setError('Please use either text prompts OR product photos, not both.');
            return;
        }
        if (!useTextPrompts && !useImagePrompts) {
            setError('Please provide either text prompts or upload product photos.');
            return;
        }

        // 2. Setup for generation
        setError(null);
        setIsLoading(true);
        setGeneratedImages([]);
        const tasks = useTextPrompts ? promptsText.trim().split('\n').filter(p => p) : productImages;
        const baseSampleAd = await fileToBase64(sampleAd);

        // 3. Loop and call API for each variation
        for (let i = 0; i < tasks.length; i++) {
            const task = tasks[i];
            const taskIdentifier = useTextPrompts ? task.substring(0, 30) : task.name;
            setCurrentTask(`Generating variation ${i + 1}/${tasks.length}: "${taskIdentifier}"`);

            try {
                let promptText = '';
                let contentParts = [{ inlineData: { mimeType: sampleAd.type, data: baseSampleAd } }];

                if (useTextPrompts) {
                    promptText = `In this image, replace the main product with "${task}". Maintain the exact same style, size, layout, background, and lighting. The new product must have realistic shadows, clean background removal, and completely cover the original product's position without flaws.`;
                } else { // useImagePrompts
                    const productImgBase64 = await fileToBase64(task);
                    contentParts.push({ inlineData: { mimeType: task.type, data: productImgBase64 } });
                    promptText = `In the first image, professionally replace the main product with the product from the second image. Maintain the original image's style, size, layout, background, and lighting. Ensure the new product has realistic shadows, clean integration, and fully covers the original product's location.`;
                }
                
                contentParts.unshift({ text: promptText });

                // Gemini API Call
                const apiKey = "";
                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key=${apiKey}`;
                
                const payload = {
                  contents: [{ parts: contentParts }],
                  generationConfig: { responseModalities: ['IMAGE'] },
                };

                let response;
                // Exponential backoff for retries
                for (let j = 0; j < 3; j++) {
                    response = await fetch(apiUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (response.ok) break;
                    await new Promise(res => setTimeout(res, 1000 * Math.pow(2, j)));
                }

                if (!response.ok) {
                    throw new Error(`API Error: ${response.statusText}`);
                }

                const result = await response.json();
                const base64Data = result?.candidates?.[0]?.content?.parts?.find(p => p.inlineData)?.inlineData?.data;
                
                if (base64Data) {
                    const imageName = useTextPrompts 
                        ? `variation-${i + 1}-prompt-${task.toLowerCase().replace(/\s+/g, '_').substring(0,20)}.png`
                        : `variation-${i + 1}-image-${task.name}`;
                    
                    setGeneratedImages(prev => [...prev, {
                        src: `data:image/png;base64,${base64Data}`,
                        name: imageName
                    }]);
                } else {
                     console.error("No image data in API response for task:", task, result);
                }

            } catch (err) {
                console.error("Generation failed for task:", task, err);
                setError(`Failed to generate variation for "${taskIdentifier}". Please try again.`);
                // Stop on first error to avoid cascading failures
                break;
            }
        }

        // 4. Cleanup
        setIsLoading(false);
        setCurrentTask('');
    };
    
    // --- Download Handlers ---
    const handleDownloadAll = async () => {
        if (typeof window.JSZip === 'undefined' || typeof window.saveAs === 'undefined') {
            setError('Could not find required libraries for downloading.');
            console.error('JSZip or FileSaver is not loaded.');
            return;
        }
        const zip = new window.JSZip();
        for (const image of generatedImages) {
            const response = await fetch(image.src);
            const blob = await response.blob();
            zip.file(image.name, blob);
        }
        zip.generateAsync({ type: 'blob' }).then(content => {
            window.saveAs(content, 'ad-variations.zip');
        });
    };
    
    const handleDownloadSingle = (image) => {
        if (type of window.saveAs === 'undefined') {
            setError('Could not find required library for downloading.');
            console.error('FileSaver is not loaded.');
            return;
        }
        window.saveAs(image.src, image.name);
    }

    // --- Render ---
    return (
        <div className="bg-gray-900 text-white min-h-screen font-sans">
            <div className="container mx-auto p-4 md:p-8">
                {/* Header */}
                <header className="text-center mb-8">
                    <h1 className="text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-500">
                        Ad Variation Builder Pro
                    </h1>
                    <p className="mt-2 text-lg text-gray-400">
                        Batch-generate ad variations with consistent style, lighting, and layout.
                    </p>
                </header>

                <main className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left Column: Inputs */}
                    <div className="flex flex-col gap-6 p-6 bg-gray-800/50 rounded-xl shadow-lg border border-gray-700">
                        <div>
                            <h2 className="text-xl font-semibold mb-3 flex items-center">
                                <span className="flex justify-center items-center h-8 w-8 rounded-full bg-blue-600 text-white font-bold mr-3">1</span>
                                Upload Sample Ad
                            </h2>
                            <div {...getSampleAdRootProps()} className="cursor-pointer">
                                <input {...getSampleAdInputProps()} />
                                {sampleAdPreview ? (
                                    <div className="relative">
                                        <img src={sampleAdPreview} alt="Sample Ad Preview" className="w-full rounded-lg object-contain max-h-60" />
                                        <button onClick={(e) => { e.stopPropagation(); setSampleAd(null); }} className="absolute top-2 right-2 bg-black/50 p-1 rounded-full text-white hover:bg-black/80 transition-colors">
                                            <XMarkIcon className="h-5 w-5" />
                                        </button>
                                    </div>
                                ) : (
                                    <UploadPlaceholder icon={<ArrowUpTrayIcon className="mx-auto h-12 w-12 text-gray-500" />} title="Click or drag file here" description="Upload the master ad poster" />
                                )}
                            </div>
                        </div>

                        <div>
                            <h2 className="text-xl font-semibold mb-3 flex items-center">
                                <span className="flex justify-center items-center h-8 w-8 rounded-full bg-blue-600 text-white font-bold mr-3">2</span>
                                Provide New Products
                            </h2>
                            <div className="space-y-4">
                                {/* Option A: Text Prompts */}
                                <div className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                                    <label htmlFor="promptsText" className="block text-sm font-medium text-gray-300 mb-2 flex items-center"><DocumentTextIcon className="h-5 w-5 mr-2"/>Use Text Prompts</label>
                                    <textarea
                                        id="promptsText"
                                        rows="4"
                                        className="w-full bg-gray-800 border-gray-600 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500 transition disabled:opacity-50"
                                        placeholder="a red running shoe&#10;a sleek silver watch&#10;a modern blue backpack"
                                        value={promptsText}
                                        onChange={handleTextChange}
                                        disabled={productImages.length > 0}
                                    />
                                    <p className="text-xs text-gray-500 mt-1">Each line will generate one ad variation.</p>
                                </div>
                                <div className="flex items-center text-gray-500">
                                    <div className="flex-grow border-t border-gray-600"></div>
                                    <span className="flex-shrink mx-4 text-sm font-semibold">OR</span>
                                    <div className="flex-grow border-t border-gray-600"></div>
                                </div>
                                {/* Option B: Image Uploads */}
                                <div className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                                     <span className="block text-sm font-medium text-gray-300 mb-2 flex items-center"><PhotoIcon className="h-5 w-5 mr-2"/>Upload Product Photos</span>
                                    <div {...getProductImagesRootProps()} className={`cursor-pointer ${promptsText.length > 0 ? 'opacity-50 pointer-events-none' : ''}`}>
                                        <input {...getProductImagesInputProps()} disabled={promptsText.length > 0} />
                                        <UploadPlaceholder icon={<PhotoIcon className="mx-auto h-12 w-12 text-gray-500" />} title="Click or drag files here" description="Each image will generate one ad" />
                                    </div>
                                    {productImagesPreview.length > 0 && (
                                        <div className="mt-4 grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                                            {productImagesPreview.map((file, i) => (
                                                <div key={i} className="relative group">
                                                    <img src={file.preview} alt={`Product ${i + 1}`} className="rounded-md object-cover aspect-square" />
                                                    <div className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <button onClick={() => removeProductImage(i)} className="text-white p-1 rounded-full hover:bg-white/20">
                                                            <XMarkIcon className="h-6 w-6" />
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Action Button */}
                        <div>
                            <button
                                onClick={handleGenerate}
                                disabled={isLoading}
                                className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-blue-500 disabled:bg-gray-500 disabled:cursor-not-allowed transition-colors"
                            >
                                {isLoading ? <Spinner /> : null}
                                {isLoading ? 'Generating...' : 'Generate Variations'}
                            </button>
                            {error && <p className="text-red-400 text-sm mt-3 text-center">{error}</p>}
                            {isLoading && currentTask && <p className="text-blue-300 text-sm mt-3 text-center animate-pulse">{currentTask}</p>}
                        </div>
                    </div>

                    {/* Right Column: Outputs */}
                    <div className="flex flex-col gap-6 p-6 bg-gray-800/50 rounded-xl shadow-lg border border-gray-700">
                         <div className="flex justify-between items-center">
                            <h2 className="text-xl font-semibold">Generated Variations</h2>
                            {generatedImages.length > 0 && (
                                <button 
                                    onClick={handleDownloadAll}
                                    className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-green-500 transition-colors">
                                    <ArrowDownTrayIcon className="h-5 w-5"/>
                                    Download All (.zip)
                                </button>
                            )}
                        </div>
                        
                        <div className="flex-grow bg-gray-900/50 rounded-lg p-4 border border-gray-700 min-h-[300px]">
                            {generatedImages.length > 0 ? (
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                    {generatedImages.map((image, index) => (
                                        <div key={index} className="group relative">
                                            <img src={image.src} alt={`Generated Variation ${index + 1}`} className="w-full rounded-md" />
                                            <div className="absolute inset-0 bg-black/70 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button 
                                                    onClick={() => handleDownloadSingle(image)}
                                                    className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
                                                     <ArrowDownTrayIcon className="h-5 w-5"/>
                                                     Download
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="flex items-center justify-center h-full text-gray-500">
                                    <p>Your generated ad variations will appear here.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}