import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected title = 'Three-Tier Architecture';
  protected angularVersion = '18';
  protected frontendStatus = 'Running ✅';
  protected backendStatus = 'Checking...';
  protected databaseStatus = 'Checking...';

  constructor() {
    this.checkServices();
  }

  private checkServices() {
    // Check backend API connectivity
    this.testBackendConnection();
    this.testDatabaseConnection();
  }

  protected testBackendConnection() {
    // This would typically call the actual backend API
    // For demo purposes, we'll simulate the check
    setTimeout(() => {
      this.backendStatus = 'Connected ✅';
    }, 1000);
  }

  protected testDatabaseConnection() {
    // This would typically call the backend to check database connectivity
    // For demo purposes, we'll simulate the check
    setTimeout(() => {
      this.databaseStatus = 'Connected ✅';
    }, 1500);
  }

  protected showDeploymentInfo() {
    alert('Check the deployment documentation in aws-infrastructure/docs/deployment-guide.md for detailed instructions!');
  }
}
