document.addEventListener('DOMContentLoaded', async () => {
    const user = await requireAuth();
    if (!user) return;
    if (user.role !== 'ADMIN') {
        window.location.href = 'index.html';
        return;
    }


    // Display Admin info in Nav
    document.getElementById('nav-name').textContent = user.name;
    const initials = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
    document.getElementById('nav-avatar').textContent = initials;

    const container = document.getElementById('profile-container');
    const viewHeader = document.getElementById('view-header');
    const editHeader = document.getElementById('edit-header');
    
    document.getElementById('btn-edit-mode').addEventListener('click', () => renderEditMode());
    document.getElementById('btn-view-mode').addEventListener('click', () => renderViewMode());

    // Basic styling rules for the grids
    const gridClass = `profile-grid`;
    const cardStyle = `background: rgba(2, 12, 6, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 24px; position: relative;`;
    const cardTitleStyle = `color: #fff; font-size: 1.1rem; font-weight: 600; margin: 0 0 20px 0; display: flex; justify-content: space-between; align-items: center;`;

    // Mock data based on admin
    const profileData = {
        name: user.name,
        role: "Professor & Director",
        email: user.email,
        username: user.email.split('@')[0],
        memberSince: "1 Aug 2021",
        regDate: "1 Aug 2021, 09:00 AM",
        lastLogin: "Today, 10:45 AM",
        dob: "12 May 1980",
        gender: "Male",
        mobile: "+91 98765 11223",
        location: "Kota, Rajasthan, India",
        bio: "Director of the Institute and Professor of Computer Science. Leading the AI integration initiatives for campus.",
        designation: "Head of Department (Computer Science)",
        empId: "EMP-2021-004",
        dept: "Computer Science & IT",
        joinDate: "1 August 2021",
        office: "Block A, Room 402",
        institute: "Institution Name (e.g. MCU)"
    };

    function renderViewMode() {
        viewHeader.style.display = 'flex';
        editHeader.style.display = 'none';

        container.innerHTML = `
            <div class="${gridClass}">
                <!-- Profile Overview -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Profile Overview</h3>
                    <div style="display: flex; gap: 20px; align-items: center;">
                        <div style="width: 100px; height: 100px; border-radius: 50%; background: #00D261; color: #041209; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: bold; position: relative;">
                            ${initials}
                            <div style="position: absolute; bottom: 0; right: 0; background: #041209; border: 1px solid rgba(255,255,255,0.2); border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: #fff;">
                                <i data-lucide="camera" style="width:16px; height:16px;"></i>
                            </div>
                        </div>
                        <div>
                            <h2 style="color: #fff; margin: 0 0 10px 0; font-size: 1.3rem;">${profileData.name}</h2>
                            <span style="background: rgba(0, 210, 97, 0.15); color: #00D261; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 6px; margin-bottom: 12px;"><i data-lucide="shield" style="width:14px; height:14px;"></i> ${profileData.role}</span>
                            <div style="display:flex; flex-direction:column; gap:6px; color:#9ca3af; font-size:0.85rem;">
                                <span style="display:flex; align-items:center; gap:8px;"><i data-lucide="mail" style="width:14px; height:14px;"></i> ${profileData.email}</span>
                                <span style="display:flex; align-items:center; gap:8px;"><i data-lucide="calendar" style="width:14px; height:14px;"></i> Member since ${profileData.memberSince}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Account Information -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Account Information</h3>
                    <div class="profile-row">
                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="user" style="width:16px; height:16px; color:#3b82f6;"></i> Full Name</div>
                        <div style="color:#fff;">${profileData.name}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="at-sign" style="width:16px; height:16px; color:#3b82f6;"></i> Username</div>
                        <div style="color:#fff;">${profileData.username}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="mail" style="width:16px; height:16px; color:#10b981;"></i> Email Address</div>
                        <div style="color:#fff; display:flex; justify-content:space-between; align-items:center;">
                            ${profileData.email}
                            <span style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem;"><i data-lucide="check" style="width:10px; height:10px;"></i> Verified</span>
                        </div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="shield" style="width:16px; height:16px; color:#f59e0b;"></i> Account Type</div>
                        <div style="color:#fff;">Administrator</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="calendar" style="width:16px; height:16px; color:#8b5cf6;"></i> Registration Date</div>
                        <div style="color:#fff;">${profileData.regDate}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="clock" style="width:16px; height:16px; color:#ec4899;"></i> Last Login</div>
                        <div style="color:#fff;">${profileData.lastLogin}</div>
                    </div>
                </div>

                <!-- Personal Details -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Personal Details <button style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#9ca3af; padding:4px 10px; border-radius:6px; font-size:0.75rem; cursor:pointer; display:flex; align-items:center; gap:6px;"><i data-lucide="edit-2" style="width:12px; height:12px;"></i> Edit</button></h3>
                    <div class="profile-row">
                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="user" style="width:16px; height:16px; color:#3b82f6;"></i> Full Name</div>
                        <div style="color:#fff;">${profileData.name}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="calendar" style="width:16px; height:16px; color:#ef4444;"></i> Date of Birth</div>
                        <div style="color:#fff;">${profileData.dob}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="users" style="width:16px; height:16px; color:#10b981;"></i> Gender</div>
                        <div style="color:#fff;">${profileData.gender}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="smartphone" style="width:16px; height:16px; color:#0ea5e9;"></i> Mobile Number</div>
                        <div style="color:#fff;">${profileData.mobile}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="map-pin" style="width:16px; height:16px; color:#f59e0b;"></i> Location</div>
                        <div style="color:#fff;">${profileData.location}</div>

                        <div style="display:flex; align-items:flex-start; gap:8px; color:#9ca3af;"><i data-lucide="file-text" style="width:16px; height:16px; color:#8b5cf6; margin-top:2px;"></i> Bio</div>
                        <div style="color:#fff; line-height: 1.4;">${profileData.bio}</div>
                    </div>
                </div>

                <!-- Staff Information -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Staff Information <button style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#9ca3af; padding:4px 10px; border-radius:6px; font-size:0.75rem; cursor:pointer; display:flex; align-items:center; gap:6px;"><i data-lucide="edit-2" style="width:12px; height:12px;"></i> Edit</button></h3>
                    <div class="profile-row">
                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="briefcase" style="width:16px; height:16px; color:#0ea5e9;"></i> Designation</div>
                        <div style="color:#fff;">${profileData.designation}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="hash" style="width:16px; height:16px; color:#10b981;"></i> Employee ID</div>
                        <div style="color:#fff;">${profileData.empId}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="building" style="width:16px; height:16px; color:#3b82f6;"></i> Department</div>
                        <div style="color:#fff;">${profileData.dept}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="calendar" style="width:16px; height:16px; color:#8b5cf6;"></i> Join Date</div>
                        <div style="color:#fff;">${profileData.joinDate}</div>
                        
                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="map-pin" style="width:16px; height:16px; color:#f59e0b;"></i> Office Room</div>
                        <div style="color:#fff;">${profileData.office}</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="library" style="width:16px; height:16px; color:#ec4899;"></i> Institute</div>
                        <div style="color:#fff;">${profileData.institute}</div>
                    </div>
                </div>

                <!-- Preferences -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Preferences <button style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#9ca3af; padding:4px 10px; border-radius:6px; font-size:0.75rem; cursor:pointer; display:flex; align-items:center; gap:6px;"><i data-lucide="edit-2" style="width:12px; height:12px;"></i> Edit</button></h3>
                    <div class="profile-row-3">
                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="globe" style="width:16px; height:16px; color:#3b82f6;"></i> Preferred Language</div>
                        <div style="color:#fff;">English (Default)</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="moon" style="width:16px; height:16px; color:#8b5cf6;"></i> Theme</div>
                        <div style="color:#fff;">Dark (Default)</div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="message-square" style="width:16px; height:16px; color:#10b981;"></i> Notify New Users</div>
                        <div style="color:#fff; display:flex; justify-content:flex-start;">
                            <div style="width:36px; height:20px; background:#00D261; border-radius:10px; position:relative;">
                                <div style="width:16px; height:16px; background:#fff; border-radius:50%; position:absolute; top:2px; right:2px;"></div>
                            </div>
                        </div>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="file-text" style="width:16px; height:16px; color:#f59e0b;"></i> Auto-Approve Docs</div>
                        <div style="color:#fff; display:flex; justify-content:flex-start;">
                            <div style="width:36px; height:20px; background:rgba(255,255,255,0.1); border-radius:10px; position:relative;">
                                <div style="width:16px; height:16px; background:#6b7280; border-radius:50%; position:absolute; top:2px; left:2px;"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Security & Access -->
                <div style="${cardStyle}">
                    <h3 style="${cardTitleStyle}">Security & Access</h3>
                    <div class="profile-row-3">
                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="lock" style="width:16px; height:16px; color:#64748b;"></i> Password</div>
                        <div style="color:#fff;">••••••••</div>
                        <button style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#fff; padding:6px 12px; border-radius:6px; font-size:0.75rem; cursor:pointer; display:flex; align-items:center; gap:6px;"><i data-lucide="unlock" style="width:14px; height:14px;"></i> Change Password</button>

                        <div style="display:flex; align-items:center; gap:8px; color:#9ca3af;"><i data-lucide="shield-check" style="width:16px; height:16px; color:#0ea5e9;"></i> Two-Factor Authentication</div>
                        <div style="color:#fff;">Not Enabled</div>
                        <button style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#fff; padding:6px 12px; border-radius:6px; font-size:0.75rem; cursor:pointer; display:flex; align-items:center; gap:6px;"><i data-lucide="shield" style="width:14px; height:14px;"></i> Enable 2FA</button>
                    </div>
                </div>
            </div>
        `;
        if (window.lucide) window.lucide.createIcons({root: container});
    }

    function renderEditMode() {
        viewHeader.style.display = 'none';
        editHeader.style.display = 'flex';

        const inputStyle = `width: 100%; padding: 8px 12px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; color: #fff; font-size: 0.85rem; outline: none; margin-top: 6px;`;
        const labelStyle = `display: block; color: #9ca3af; font-size: 0.8rem;`;
        
        container.innerHTML = `
            <div class="${gridClass}">
                <!-- Profile Photo -->
                <div style="${cardStyle} grid-column: span 1;">
                    <h3 style="${cardTitleStyle}">Profile Photo</h3>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 20px;">
                        <div style="width: 150px; height: 150px; border-radius: 50%; background: #00D261; color: #041209; display: flex; align-items: center; justify-content: center; font-size: 4rem; font-weight: bold; position: relative;">
                            ${initials}
                            <div style="position: absolute; bottom: 5px; right: 5px; background: #041209; border: 1px solid rgba(255,255,255,0.2); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; color: #fff; cursor:pointer;">
                                <i data-lucide="camera" style="width:20px; height:20px;"></i>
                            </div>
                        </div>
                        <button class="btn-outline-small" style="width: 100%; max-width: 200px; display:flex; justify-content:center; gap:8px; color:#00D261; border-color:rgba(0,210,97,0.3);"><i data-lucide="upload" style="width:16px; height:16px;"></i> Change Photo</button>
                        <span style="color: #6b7280; font-size: 0.75rem;">Supported formats: JPG, PNG (Max 5MB)</span>
                    </div>
                </div>

                <!-- Personal Information -->
                <div style="${cardStyle} grid-column: span 2;">
                    <h3 style="${cardTitleStyle}"><span style="display:flex; align-items:center; gap:8px;"><i data-lucide="user" style="color:#3b82f6;"></i> Personal Information</span></h3>
                    <p style="color:#9ca3af; font-size:0.8rem; margin-top:-15px; margin-bottom:20px;">Update your basic details.</p>
                    
                    <div class="profile-row-2">
                        <div><label style="${labelStyle}">Full Name <span style="color:#ef4444">*</span></label><input type="text" value="${profileData.name}" style="${inputStyle}"></div>
                        <div>
                            <label style="${labelStyle}">Email Address <span style="color:#ef4444">*</span></label>
                            <div style="position:relative;">
                                <input type="email" value="${profileData.email}" disabled style="${inputStyle} background:rgba(0,0,0,0.2); color:#6b7280; border-color:rgba(255,255,255,0.05);">
                                <span style="position:absolute; right:10px; top:12px; background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 2px 8px; border-radius: 12px; font-size: 0.65rem;"><i data-lucide="check" style="width:10px; height:10px;"></i> Verified</span>
                            </div>
                        </div>
                        
                        <div><label style="${labelStyle}">Date of Birth <span style="color:#ef4444">*</span></label><input type="date" value="1980-05-12" style="${inputStyle}"></div>
                        <div><label style="${labelStyle}">Alternate Email (Optional)</label><input type="email" placeholder="e.g. alternate@gmail.com" style="${inputStyle}"></div>
                        
                        <div>
                            <label style="${labelStyle}">Gender <span style="color:#ef4444">*</span></label>
                            <select style="${inputStyle}">
                                <option value="Male" selected>Male</option>
                                <option value="Female">Female</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div><label style="${labelStyle}">Location <span style="color:#ef4444">*</span></label><input type="text" value="${profileData.location}" style="${inputStyle}"></div>
                        
                        <div><label style="${labelStyle}">Mobile Number <span style="color:#ef4444">*</span></label><input type="text" value="${profileData.mobile}" style="${inputStyle}"></div>
                        <div><label style="${labelStyle}">Bio / About You</label><textarea style="${inputStyle} height: 80px; resize:none;">${profileData.bio}</textarea><div style="text-align:right; font-size:0.7rem; color:#6b7280; margin-top:4px;">110/200</div></div>
                    </div>
                </div>

                <!-- Staff Information -->
                <div style="${cardStyle} grid-column: span 2;">
                    <h3 style="${cardTitleStyle}"><span style="display:flex; align-items:center; gap:8px;"><i data-lucide="briefcase" style="color:#8b5cf6;"></i> Staff Information</span></h3>
                    <p style="color:#9ca3af; font-size:0.8rem; margin-top:-15px; margin-bottom:20px;">Update your professional details.</p>
                    
                    <div class="profile-row-2">
                        <div>
                            <label style="${labelStyle}">Designation <span style="color:#ef4444">*</span></label>
                            <input type="text" value="${profileData.designation}" style="${inputStyle}">
                        </div>
                        <div>
                            <label style="${labelStyle}">Employee ID <span style="color:#ef4444">*</span></label>
                            <input type="text" value="${profileData.empId}" disabled style="${inputStyle} background:rgba(0,0,0,0.2); color:#6b7280;">
                        </div>
                        
                        <div><label style="${labelStyle}">Department <span style="color:#ef4444">*</span></label><input type="text" value="${profileData.dept}" disabled style="${inputStyle} background:rgba(0,0,0,0.2); color:#6b7280;"></div>
                        <div><label style="${labelStyle}">Office / Cabin <span style="color:#ef4444">*</span></label><input type="text" value="${profileData.office}" style="${inputStyle}"></div>
                        
                        <div><label style="${labelStyle}">Join Date <span style="color:#ef4444">*</span></label><input type="text" value="${profileData.joinDate}" disabled style="${inputStyle} background:rgba(0,0,0,0.2); color:#6b7280;"></div>
                        <div>
                            <label style="${labelStyle}">Institution / University <span style="color:#ef4444">*</span></label>
                            <input type="text" value="${profileData.institute}" disabled style="${inputStyle} background:rgba(0,0,0,0.2); color:#6b7280;">
                        </div>
                    </div>
                </div>

                <!-- Preferences -->
                <div style="${cardStyle} grid-column: span 1;">
                    <h3 style="${cardTitleStyle}"><span style="display:flex; align-items:center; gap:8px;"><i data-lucide="settings" style="color:#10b981;"></i> Preferences</span></h3>
                    <p style="color:#9ca3af; font-size:0.8rem; margin-top:-15px; margin-bottom:20px;">Set your administrative preferences.</p>
                    
                    <div class="profile-row-2" style="margin-bottom: 20px;">
                        <div>
                            <label style="${labelStyle}">Preferred Language <span style="color:#ef4444">*</span></label>
                            <select style="${inputStyle}">
                                <option selected>English (Default)</option>
                            </select>
                        </div>
                        <div>
                            <label style="${labelStyle}">Theme</label>
                            <select style="${inputStyle}">
                                <option selected>Dark (Default)</option>
                            </select>
                        </div>
                    </div>
                    
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; padding:12px; background:rgba(255,255,255,0.02); border-radius:8px;">
                        <div>
                            <div style="color:#fff; font-size:0.85rem; font-weight:500;">Notify New Users</div>
                            <div style="color:#9ca3af; font-size:0.75rem;">Get alerted when new students join</div>
                        </div>
                        <div style="width:36px; height:20px; background:#00D261; border-radius:10px; position:relative; cursor:pointer;">
                            <div style="width:16px; height:16px; background:#fff; border-radius:50%; position:absolute; top:2px; right:2px;"></div>
                        </div>
                    </div>

                    <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(255,255,255,0.02); border-radius:8px;">
                        <div>
                            <div style="color:#fff; font-size:0.85rem; font-weight:500;">Auto-Approve Docs</div>
                            <div style="color:#9ca3af; font-size:0.75rem;">Skip manual review for uploads</div>
                        </div>
                        <div style="width:36px; height:20px; background:rgba(255,255,255,0.1); border-radius:10px; position:relative; cursor:pointer;">
                            <div style="width:16px; height:16px; background:#6b7280; border-radius:50%; position:absolute; top:2px; left:2px;"></div>
                        </div>
                    </div>
                </div>

                <!-- Security & Privacy Container -->
                <div style="grid-column: span 1; display:flex; flex-direction:column; gap:20px;">
                    <!-- Security -->
                    <div style="${cardStyle}">
                        <h3 style="${cardTitleStyle}"><span style="display:flex; align-items:center; gap:8px;"><i data-lucide="lock" style="color:#f59e0b;"></i> Security</span></h3>
                        <p style="color:#9ca3af; font-size:0.8rem; margin-top:-15px; margin-bottom:20px;">Manage your admin account security.</p>
                        
                        <div style="display: flex; flex-direction: column; gap: 15px;">
                            <div style="position:relative;">
                                <label style="${labelStyle}">Current Password</label>
                                <input type="password" placeholder="Enter current password" style="${inputStyle}">
                                <i data-lucide="eye" style="position:absolute; right:12px; bottom:10px; width:16px; color:#6b7280; cursor:pointer;"></i>
                            </div>
                            <div style="position:relative;">
                                <label style="${labelStyle}">New Password</label>
                                <input type="password" placeholder="Enter new password" style="${inputStyle}">
                                <i data-lucide="eye" style="position:absolute; right:12px; bottom:10px; width:16px; color:#6b7280; cursor:pointer;"></i>
                            </div>
                            <div style="position:relative;">
                                <label style="${labelStyle}">Confirm New Password</label>
                                <input type="password" placeholder="Confirm new password" style="${inputStyle}">
                                <i data-lucide="eye" style="position:absolute; right:12px; bottom:10px; width:16px; color:#6b7280; cursor:pointer;"></i>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Actions -->
                <div style="grid-column: 1 / -1; display:flex; justify-content:flex-end; gap:15px; margin-top:10px;">
                    <button class="btn-outline-small" onclick="document.getElementById('btn-view-mode').click()" style="padding: 10px 24px; font-size:0.9rem;">Cancel</button>
                    <button class="btn-green" style="padding: 10px 24px; display:flex; gap:8px; align-items:center; font-size:0.9rem;"><i data-lucide="save" style="width:16px; height:16px;"></i> Save Changes</button>
                </div>

            </div>
        `;
        if (window.lucide) window.lucide.createIcons({root: container});
    }

    // Default to view mode
    renderViewMode();
});
