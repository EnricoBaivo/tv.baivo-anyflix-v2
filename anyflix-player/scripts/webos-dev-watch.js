#!/usr/bin/env node

import { spawn } from 'child_process';
import { watch } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = resolve(__dirname, '..');

let isPackaging = false;
let pendingReload = false;
let debounceTimer = null;

console.log('🚀 Starting WebOS development mode...\n');

// Start Vite build in watch mode
console.log('📦 Starting Vite build watcher...');
const viteBuild = spawn('npm', ['run', 'dev:webos'], {
  cwd: projectRoot,
  shell: true,
  stdio: 'inherit'
});

viteBuild.on('error', (err) => {
  console.error('❌ Failed to start Vite build:', err);
  process.exit(1);
});

// Watch dist folder for changes
const distPath = resolve(projectRoot, 'dist');

console.log('👀 Watching dist folder for changes...\n');
console.log('─'.repeat(60));

const watcher = watch(distPath, { recursive: true }, (eventType, filename) => {
  if (!filename) return;

  // Debounce: wait for all build files to be written
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (!isPackaging) {
      pendingReload = false;
      packageAndInstall();
    } else {
      pendingReload = true;
    }
  }, 1000); // Wait 1 second after last change
});

async function packageAndInstall() {
  isPackaging = true;

  console.log('\n📦 Changes detected! Packaging and installing...');
  console.log('─'.repeat(60));

  try {
    // Package the dist folder
    console.log('📦 Packaging...');
    await runCommand('npm', ['run', 'package']);

    // Install to emulator
    console.log('📲 Installing to emulator...');
    await runCommand('npm', ['run', 'lg-install:emulator']);

    // Launch the app
    console.log('🚀 Launching app...');
    await runCommand('npm', ['run', 'launch:emulator']);

    console.log('✅ Successfully deployed to emulator!');
    console.log('─'.repeat(60));
    console.log('👀 Watching for changes...\n');

  } catch (error) {
    console.error('❌ Error during deployment:', error.message);
    console.log('─'.repeat(60));
    console.log('👀 Watching for changes...\n');
  }

  isPackaging = false;

  // If changes happened during packaging, trigger another reload
  if (pendingReload) {
    pendingReload = false;
    packageAndInstall();
  }
}

function runCommand(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: projectRoot,
      shell: true,
      stdio: 'inherit'
    });

    child.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });

    child.on('error', (err) => {
      reject(err);
    });
  });
}

// Handle cleanup
process.on('SIGINT', () => {
  console.log('\n\n🛑 Stopping WebOS development mode...');
  watcher.close();
  viteBuild.kill();
  process.exit(0);
});

process.on('SIGTERM', () => {
  watcher.close();
  viteBuild.kill();
  process.exit(0);
});

console.log('💡 Press Ctrl+C to stop\n');
